import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
    try {
        const projectRoot = path.resolve(process.cwd(), '..');
        const csvPath = path.join(projectRoot, '.tmp/live_retail_sales.csv');
        const darazPath = path.join(projectRoot, 'execution/daraz_electronics.json');
        const priceoyePath = path.join(projectRoot, 'execution/priceoye_electronics.json');

        let allData: any[] = [];

        const darazAffId = process.env.DARAZ_AFFILIATE_ID || "";
        const priceoyeAffId = process.env.PRICEOYE_AFFILIATE_ID || "";

        // 1. Process CSV Data (clothing and shoes)
        if (fs.existsSync(csvPath)) {
            try {
                const fileContent = fs.readFileSync(csvPath, 'utf-8');
                const lines = fileContent.trim().split('\n');
                if (lines.length >= 2) {
                    // Parse CSV properly handling quoted fields
                    const parseCSVLine = (line: string): string[] => {
                        const result: string[] = [];
                        let current = '';
                        let inQuotes = false;
                        
                        for (let i = 0; i < line.length; i++) {
                            const char = line[i];
                            if (char === '"') {
                                inQuotes = !inQuotes;
                            } else if (char === ',' && !inQuotes) {
                                result.push(current.trim());
                                current = '';
                            } else {
                                current += char;
                            }
                        }
                        result.push(current.trim());
                        return result;
                    };
                    
                    const headers = parseCSVLine(lines[0]);
                    const csvData = lines.slice(1)
                        .filter(line => line.trim().length > 0)
                        .map(line => {
                            const values = parseCSVLine(line);
                            const entry: any = {};
                            headers.forEach((header, index) => {
                                let val = values[index] ? values[index].replace(/^"|"$/g, '').trim() : '';
                                entry[header] = val;
                            });
                            // Normalize discount percentage format to match electronics data (add - prefix if missing)
                            if (entry["Discount Percentage"] && !entry["Discount Percentage"].startsWith('-')) {
                                entry["Discount Percentage"] = `-${entry["Discount Percentage"]}`;
                            }
                            return entry;
                        });
                    allData = [...csvData];
                    console.log(`Loaded ${csvData.length} items from CSV (clothing/shoes)`);
                }
            } catch (csvError) {
                console.error("Error parsing CSV:", csvError);
            }
        } else {
            console.log(`CSV file not found at ${csvPath}. Run scraper to generate clothing/shoes data.`);
        }

        // 2. Process Daraz JSON Data
        if (fs.existsSync(darazPath)) {
            const darazRaw = fs.readFileSync(darazPath, 'utf-8');
            const darazJson = JSON.parse(darazRaw);

            const darazItems = darazJson.map((item: any) => {
                let url = item.product_url;
                if (darazAffId && !url.includes('aff_id')) {
                    const separator = url.includes('?') ? '&' : '?';
                    url += `${separator}aff_id=${darazAffId}`;
                }

                return {
                    "Brand Name": item.name.length > 30 ? item.name.substring(0, 30) + "..." : item.name,
                    "Category": item.category === "Mobiles" ? "Mobile" : (item.category || "Electronics"),
                    "Discount Percentage": `-${item.discount_percentage}%`,
                    "Source": "Daraz Real-time",
                    "URL": url,
                    "ImageURL": item.image_url,
                    "FullTitle": item.name,
                    "Rating": item.rating,
                    "Reviews": item.reviews,
                    "Price": item.sale_price,
                    "OriginalPrice": item.original_price
                };
            });
            allData = [...allData, ...darazItems];
        }

        // 3. Process PriceOye JSON Data
        if (fs.existsSync(priceoyePath)) {
            const priceoyeRaw = fs.readFileSync(priceoyePath, 'utf-8');
            const priceoyeJson = JSON.parse(priceoyeRaw);

            const priceoyeItems = priceoyeJson.map((item: any) => {
                let url = item.product_url;
                if (priceoyeAffId) {
                    const separator = url.includes('?') ? '&' : '?';
                    url += `${separator}utm_source=aff_retail_monitor&utm_medium=affiliate&aff_id=${priceoyeAffId}`;
                }

                return {
                    "Brand Name": item.name.length > 30 ? item.name.substring(0, 30) + "..." : item.name,
                    "Category": (item.category === "Mobiles" || item.category === "Smart Phones" || item.category === "Mobile") ? "Mobile" : item.category,
                    "Discount Percentage": `-${item.discount_percentage}%`,
                    "Source": "PriceOye Real-time",
                    "URL": url,
                    "ImageURL": item.image_url,
                    "FullTitle": item.name,
                    "Price": item.sale_price,
                    "OriginalPrice": item.original_price
                };
            });
            allData = [...allData, ...priceoyeItems];
        }

        return NextResponse.json(allData);
    } catch (e: any) {
        console.error("Error reading sales data:", e);
        return NextResponse.json({ error: String(e) }, { status: 500 });
    }
}
