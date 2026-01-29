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

        // 1. Process CSV Data
        if (fs.existsSync(csvPath)) {
            const fileContent = fs.readFileSync(csvPath, 'utf-8');
            const lines = fileContent.trim().split('\n');
            if (lines.length >= 2) {
                const headers = lines[0].split(',').map(h => h.trim());
                const csvData = lines.slice(1).map(line => {
                    const values = line.split(',');
                    const entry: any = {};
                    headers.forEach((header, index) => {
                        const val = values[index] ? values[index].trim() : '';
                        entry[header] = val;
                    });
                    return entry;
                });
                allData = [...csvData];
            }
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
