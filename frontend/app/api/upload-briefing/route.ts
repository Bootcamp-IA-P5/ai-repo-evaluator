import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

// Server-side directory where briefing PDFs are saved.
// The host folder ./briefings is mounted as /data/briefings in both containers,
// so saving a file here makes it immediately visible to the backend container.
const BRIEFINGS_DIR = process.env.BRIEFINGS_DIR ?? '/data/briefings';

export async function POST(req: NextRequest): Promise<NextResponse> {
  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json({ success: false, message: 'Invalid form data' }, { status: 400 });
  }

  const file = formData.get('file');
  if (!(file instanceof File)) {
    return NextResponse.json({ success: false, message: 'No file provided' }, { status: 400 });
  }

  // Allow only PDF files.
  if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
    return NextResponse.json({ success: false, message: 'Only PDF files are accepted' }, { status: 415 });
  }

  // Sanitise the filename to prevent path traversal attacks.
  const safeName = path.basename(file.name).replace(/[^a-zA-Z0-9._-]/g, '_');
  if (!safeName) {
    return NextResponse.json({ success: false, message: 'Invalid file name' }, { status: 400 });
  }

  const destination = path.join(BRIEFINGS_DIR, safeName);

  // Ensure the target directory exists (important on first run / fresh clone).
  await mkdir(BRIEFINGS_DIR, { recursive: true });

  const buffer = Buffer.from(await file.arrayBuffer());
  await writeFile(destination, buffer);

  return NextResponse.json({
    success: true,
    data: { path: destination, name: safeName },
  });
}
