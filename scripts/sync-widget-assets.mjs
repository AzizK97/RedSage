import { promises as fs } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const repoRoot = process.cwd();
const widgetDist = path.resolve(repoRoot, 'frontend/redmineAgentUI/dist-widget');
const pluginAssetsRoot = path.resolve(repoRoot, 'plugins/redmine_ai_chat_widget/assets');
const targets = [
  {
    source: path.join(widgetDist, 'chat-widget.js'),
    target: path.join(pluginAssetsRoot, 'javascripts/chat-widget.js'),
  },
  {
    source: path.join(widgetDist, 'chat-widget.css'),
    target: path.join(pluginAssetsRoot, 'stylesheets/chat-widget.css'),
  },
];

async function copyFileWithDirs(source, target) {
  await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.copyFile(source, target);
  console.log(`Copied ${path.relative(repoRoot, source)} -> ${path.relative(repoRoot, target)}`);
}

async function main() {
  for (const entry of targets) {
    await copyFileWithDirs(entry.source, entry.target);
  }
}

main().catch((error) => {
  console.error('[sync-widget-assets] Failed to copy widget assets:', error);
  process.exitCode = 1;
});
