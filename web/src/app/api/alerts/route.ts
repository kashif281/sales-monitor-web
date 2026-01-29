import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

const projectRoot = path.resolve(process.cwd(), '..');
const ALERTS_FILE = path.join(projectRoot, 'execution/alerts.json');
const EMAIL_SCRIPT = path.join(projectRoot, 'execution/send_email_alert.py');

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { email, category, minDiscount, keywords } = body;

        if (!email) {
            return NextResponse.json({ error: 'Email is required' }, { status: 400 });
        }

        let alerts = [];
        if (fs.existsSync(ALERTS_FILE)) {
            const raw = fs.readFileSync(ALERTS_FILE, 'utf-8');
            alerts = JSON.parse(raw);
        }

        const newAlert = {
            id: Date.now(),
            email,
            category: category || 'All',
            minDiscount: minDiscount || 0,
            keywords: keywords || '',
            createdAt: new Date().toISOString()
        };

        alerts.push(newAlert);
        fs.writeFileSync(ALERTS_FILE, JSON.stringify(alerts, null, 2));

        // Trigger confirmation email
        exec(`python "${EMAIL_SCRIPT}" --confirm "${email}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Email Trigger Error: ${error.message}`);
                return;
            }
            console.log(`Email Trigger Success: ${stdout}`);
        });

        return NextResponse.json({ message: 'Subscription successful', alert: newAlert });
    } catch (error) {
        console.error('Error saving alert:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}

export async function GET() {
    try {
        if (!fs.existsSync(ALERTS_FILE)) {
            return NextResponse.json([]);
        }
        const raw = fs.readFileSync(ALERTS_FILE, 'utf-8');
        const alerts = JSON.parse(raw);
        return NextResponse.json(alerts);
    } catch (error) {
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
