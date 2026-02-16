import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/db/index.js';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { fileURLToPath } from 'url';

async function main() {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = join(__filename, '..');
    const filePath = join(__dirname, '../secret/_secrets.json');

    async function getSecrets() {
        try {
            const data = await readFile(filePath, 'utf8');
            return JSON.parse(data);
        } catch (err) {
            console.error('Error reading or parsing file:', err);
            process.exit(1);
        }
    }

    const userAgent = 'post@benkku.com';
    const client = createClient(dbnavProfile, userAgent);
    const secrets = await getSecrets();
    
    try {
        const result = await client.journeys(secrets.QP_COMMUTE_FROM_OBJECT, secrets.QP_COMMUTE_TO_OBJECT, { results: 3, stopovers: true });
        process.stdout.write(JSON.stringify(result));
    } catch (error) {
        console.error('Error fetching journey data: ', error);
        process.exit(1);
    }
	process.exit(0);
}

main();
