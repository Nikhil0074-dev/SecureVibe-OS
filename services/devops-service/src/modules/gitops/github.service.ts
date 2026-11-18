import { Octokit } from "@octokit/rest";

/** Create a repo for the authenticated user and push the generated files. Token comes from env/Vault, never from the client. */
export async function pushToGithub(repoName: string, files: Record<string, string>, token = process.env.GITHUB_TOKEN) {
  if (!token) throw new Error("GITHUB_TOKEN not configured");
  if (!/^[A-Za-z0-9._-]{1,100}$/.test(repoName)) throw new Error("invalid repo name");
  const octokit = new Octokit({ auth: token });
  const { data: repo } = await octokit.repos.createForAuthenticatedUser({ name: repoName, private: true, auto_init: true });
  for (const [path, content] of Object.entries(files)) {
    await octokit.repos.createOrUpdateFileContents({
      owner: repo.owner.login, repo: repo.name, path,
      message: `securevibe: add ${path}`, content: Buffer.from(content).toString("base64"),
    });
  }
  return { url: repo.html_url };
}
