# GitHub Pages Setup Instructions

This document explains how to configure GitHub Pages for the Earning Robot demonstration website.

## 📋 Prerequisites

- Repository must be public (or GitHub Pro account for private repo Pages)
- You must have admin access to the repository
- The website files must be in the `/website` directory

## ⚙️ Configuration Steps

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** (⚙️ icon in the top menu)
3. In the left sidebar, click on **Pages** (under "Code and automation")
4. Under **Source**, select:
   - Source: **GitHub Actions**
   
   (Note: The workflow will automatically deploy to GitHub Pages when triggered)

### 2. Configure Actions Permissions

1. Still in **Settings**, click on **Actions** → **General** in the left sidebar
2. Under **Workflow permissions**, ensure:
   - ✅ **Read and write permissions** is selected
   - ✅ **Allow GitHub Actions to create and approve pull requests** is checked

3. Click **Save**

### 3. Trigger the Deployment

The website will automatically deploy when:
- Changes are pushed to the `main` branch in the `website/` directory
- The workflow is manually triggered

To manually trigger:
1. Go to **Actions** tab in your repository
2. Click on **Deploy Website to GitHub Pages** workflow
3. Click **Run workflow** → **Run workflow**

### 4. Verify Deployment

1. After the workflow completes (usually 1-2 minutes), go to **Settings** → **Pages**
2. You should see: **"Your site is live at https://YOUR_USERNAME.github.io/robot/"**
3. Click the link to view your website

## 🔧 Troubleshooting

### Pages not showing up

**Problem:** GitHub Pages section shows "Pages settings are currently being created"

**Solution:** Wait a few minutes and refresh the page. It can take up to 10 minutes for Pages to be fully set up.

---

**Problem:** Website shows 404 error

**Solution:** 
- Ensure the workflow ran successfully (check Actions tab)
- Verify the `gh-pages` branch was created
- Check that the deployment completed without errors

---

**Problem:** Workflow fails with permissions error

**Solution:**
- Go to Settings → Actions → General
- Ensure workflow permissions are set to "Read and write"
- Try running the workflow again

---

**Problem:** CSS/JS not loading

**Solution:**
- Check that `baseurl: "/robot"` is set correctly in `website/_config.yml`
- Verify asset paths use `{{ '/assets/...' | relative_url }}`
- Clear browser cache and hard refresh (Ctrl+F5)

---

**Problem:** Changes not appearing on website

**Solution:**
- Ensure changes were committed and pushed to `main` branch
- Check Actions tab to see if workflow was triggered
- Wait for deployment to complete (check workflow status)
- Clear browser cache

## 🌐 Custom Domain (Optional)

To use a custom domain:

1. **Add CNAME file:**
   - Create `website/CNAME` file
   - Add your domain: `example.com`

2. **Configure DNS:**
   - Add these A records to your DNS provider:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```
   - Or add CNAME record pointing to `YOUR_USERNAME.github.io`

3. **Update repository settings:**
   - Go to Settings → Pages
   - Enter your custom domain
   - Enable "Enforce HTTPS"

4. **Update baseurl:**
   - Edit `website/_config.yml`
   - Change `baseurl: ""` (empty for custom domain)
   - Change `url: "https://example.com"`

## 📝 Workflow Details

The deployment workflow (`deploy-website.yml`) does the following:

1. **Checkout code** - Gets repository files
2. **Setup Ruby** - Installs Ruby 3.1
3. **Install Jekyll** - Installs Jekyll gem
4. **Setup Pages** - Configures GitHub Pages
5. **Build site** - Runs `jekyll build` in website directory
6. **Upload artifact** - Packages built site
7. **Deploy** - Publishes to GitHub Pages

The workflow runs:
- On push to `main` branch (when `website/**` files change)
- Manually via Actions tab (workflow_dispatch)

## 🔄 Making Updates

To update the website:

1. **Edit files** in `website/` directory locally
2. **Test locally** (optional):
   ```bash
   cd website
   jekyll build
   # Or serve locally
   jekyll serve
   ```
3. **Commit changes**:
   ```bash
   git add website/
   git commit -m "Update website content"
   git push origin main
   ```
4. **Wait for deployment** - Check Actions tab for progress
5. **Verify changes** - Visit your GitHub Pages URL

## 📚 Related Documentation

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## ✅ Verification Checklist

After setup, verify:

- [ ] GitHub Pages is enabled in repository settings
- [ ] Workflow permissions are set to read/write
- [ ] Deployment workflow ran successfully
- [ ] Website is accessible at GitHub Pages URL
- [ ] All pages load correctly
- [ ] Navigation works
- [ ] Demo panel is interactive
- [ ] CSS styling is applied
- [ ] JavaScript functions work
- [ ] Links to GitHub repository work
- [ ] Mobile responsive design works

---

**Need help?** Open an issue in the repository or check the [GitHub Pages documentation](https://docs.github.com/en/pages).
