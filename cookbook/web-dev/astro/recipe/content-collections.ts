import { getCollection, getEntry, defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const docSchema = z.object({
  title: z.string(),
  tags: z.array(z.string()).default([]),
  draft: z.boolean().default(false),
  publishedAt: z.coerce.date(),
});

const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/docs' }),
  schema: docSchema,
});

export const collections = { docs };

type DocFrontmatter = z.infer<typeof docSchema>;

export type DocEntry = {
  id: string;
  data: DocFrontmatter;
  body: string;
};

export async function listPublishedDocs(): Promise<DocEntry[]> {
  const entries = await getCollection('docs', (entry) => !entry.data.draft);
  return entries
    .map((entry) => ({
      id: entry.id,
      data: entry.data,
      body: entry.body,
    }))
    .sort((a, b) => b.data.publishedAt.getTime() - a.data.publishedAt.getTime());
}

export async function findDoc(slug: string): Promise<DocEntry | null> {
  const entry = await getEntry('docs', slug);
  if (!entry) return null;
  return { id: entry.id, data: entry.data, body: entry.body };
}

async function demo() {
  const published = await listPublishedDocs();
  console.log(`Published docs: ${published.length}`);
  for (const doc of published) {
    console.log(`- [${doc.id}] ${doc.data.title} (${doc.data.tags.join(', ')})`);
  }
  const single = await findDoc('getting-started');
  if (single) {
    console.log(`Found: ${single.data.title} @ ${single.data.publishedAt.toISOString()}`);
  }
}

export { demo };