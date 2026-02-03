import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';

export async function POST(): Promise<NextResponse> {
    try {
        // Path to the python script relative to web/ root
        const scriptPath = path.resolve(process.cwd(), '../execution/scrape_retailers.py');
        const projectRoot = path.resolve(process.cwd(), '..');

        console.log(`Running scraper at: ${scriptPath}`);

        return new Promise<NextResponse>((resolve) => {
            const darazScript = path.resolve(process.cwd(), '../execution/scrape_daraz_electronics.py');

            console.log(`Running main scraper: ${scriptPath}`);

            exec(`python "${scriptPath}"`, { cwd: projectRoot }, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Retail Scraper Error: ${error}`);
                }

                console.log(`Running Daraz scraper: ${darazScript}`);
                exec(`python "${darazScript}"`, { cwd: projectRoot }, (dError, dStdout, dStderr) => {
                    if (dError) {
                        console.error(`Daraz Scraper Error: ${dError}`);
                    }

                    const priceoyeScript = path.resolve(process.cwd(), '../execution/scrape_priceoye_electronics.py');
                    console.log(`Running PriceOye scraper: ${priceoyeScript}`);
                    exec(`python "${priceoyeScript}"`, { cwd: projectRoot }, (pError, pStdout, pStderr) => {
                        if (pError) {
                            console.error(`PriceOye Scraper Error: ${pError}`);
                        }

                        resolve(NextResponse.json({
                            success: true,
                            log: stdout + "\n" + dStdout + "\n" + pStdout,
                            darazLog: dStdout,
                            priceoyeLog: pStdout
                        }));
                    });
                });
            });
        });
    } catch (e: any) {
        console.error("API Error:", e);
        return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
    }
}
