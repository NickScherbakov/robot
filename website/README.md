# Earning Robot - Demonstration Website

This directory contains the demonstration website for the Earning Robot project, built with Jekyll and deployed via GitHub Pages.

## 🌐 Live Website

Visit the live demo at: [https://nickscherbakov.github.io/robot/](https://nickscherbakov.github.io/robot/)

## 📁 Structure

```
website/
├── _layouts/           # HTML layouts
│   └── default.html   # Main page layout
├── _includes/         # Reusable components (if needed)
├── assets/
│   ├── css/
│   │   └── style.css  # Main stylesheet
│   ├── js/
│   │   └── main.js    # Interactive demo JavaScript
│   └── images/        # Images and icons
├── _config.yml        # Jekyll configuration
├── index.html         # Home page
└── README.md          # This file
```

## 🎯 Website Features

### Pages & Sections

1. **Hero Section**
   - Eye-catching slogan: "Autonomous earning robot — privacy, ethics, profit"
   - Clear call-to-action buttons
   - Quick navigation to demo and GitHub

2. **Mission Statement**
   - Privacy-first approach
   - Full autonomy
   - Profit tracking
   - Open source commitment

3. **How It Works**
   - Visual architecture diagram
   - Layer-by-layer explanation
   - Step-by-step workflow
   - Easy to understand for non-technical users

4. **Advantages**
   - Complete autonomy
   - Privacy & security
   - Ethical operations
   - Easy extensibility
   - Financial transparency
   - Simple deployment

5. **Interactive Demo**
   - Live chat simulation
   - Real-time financial flow visualization
   - Task counting
   - Revenue/expense tracking
   - Profit calculation

6. **Call to Action**
   - Links to GitHub repository
   - Quick start guide
   - Documentation
   - Support options

7. **Features Summary**
   - AI integration capabilities
   - Payment system features
   - Control interfaces
   - Reporting features

## 🚀 Local Development

### Prerequisites

- Ruby 2.7 or higher
- Bundler gem
- Jekyll gem

### Setup

1. **Install dependencies**
   ```bash
   cd website
   
   # Install Ruby gems
   gem install bundler jekyll
   bundle install
   ```

2. **Run local server**
   ```bash
   bundle exec jekyll serve
   ```

3. **View in browser**
   Open http://localhost:4000/robot/

### Development Tips

- Jekyll auto-rebuilds when files change
- Refresh browser to see updates
- Check `_site/` directory for built files (not committed to git)
- Customize `_config.yml` for site settings

## 📦 Building

To build the site manually:

```bash
bundle exec jekyll build
```

The built site will be in the `_site/` directory.

## 🚢 Deployment

### Automatic Deployment (GitHub Actions)

The website is automatically deployed to GitHub Pages when changes are pushed to the main branch.

The deployment workflow:
1. Triggered on push to main branch
2. Builds Jekyll site
3. Deploys to `gh-pages` branch
4. Available at GitHub Pages URL

### Manual Deployment

If needed, you can deploy manually:

1. Build the site:
   ```bash
   bundle exec jekyll build
   ```

2. The `_site/` directory contains the built website

3. Deploy `_site/` contents to your hosting provider

## ⚙️ Configuration

Edit `_config.yml` to customize:

- **Site title**: Change the website title
- **Description**: Update meta description
- **baseurl**: Adjust for different repository name
- **url**: Change for custom domain

Example:
```yaml
title: "Your Robot Name"
description: "Your custom description"
baseurl: "/your-repo-name"
url: "https://yourusername.github.io"
```

## 🎨 Customization

### Colors

Edit CSS variables in `assets/css/style.css`:

```css
:root {
    --primary-color: #4CAF50;    /* Main brand color */
    --secondary-color: #2196F3;  /* Secondary actions */
    --accent-color: #FF9800;     /* Highlights */
    /* ... */
}
```

### Content

- **Hero section**: Edit in `index.html` (`.hero` section)
- **Mission**: Update in `index.html` (`.mission-grid`)
- **Features**: Modify in `index.html` (`.advantages-grid`)

### Demo Behavior

Customize the demo in `assets/js/main.js`:

```javascript
// Change pricing
const TASK_PRICE = 0.50;  // Revenue per task
const AI_COST = 0.02;     // Expense per task

// Add custom responses
const sampleResponses = [
    "Your custom response here",
    // ...
];
```

## 🔧 Troubleshooting

### Site not loading locally

- Ensure Ruby and Jekyll are installed correctly
- Run `bundle install` to install dependencies
- Check for port conflicts (default: 4000)

### GitHub Pages not updating

- Check GitHub Actions workflow status
- Verify `gh-pages` branch exists
- Ensure GitHub Pages is enabled in repository settings
- Wait a few minutes for propagation

### Styling issues

- Clear browser cache
- Check browser console for errors
- Verify CSS file is loading
- Check for CSS syntax errors

### JavaScript not working

- Open browser console to check for errors
- Verify JS file is loading correctly
- Check that DOM elements exist before accessing them

## 📝 Adding New Sections

To add a new section to the homepage:

1. **Add HTML** in `index.html`:
   ```html
   <section id="new-section" class="section">
     <div class="container">
       <h2>New Section Title</h2>
       <!-- Your content -->
     </div>
   </section>
   ```

2. **Add styling** in `assets/css/style.css`:
   ```css
   #new-section {
       /* Your styles */
   }
   ```

3. **Add navigation** link in `_layouts/default.html`:
   ```html
   <li><a href="#new-section">New Section</a></li>
   ```

## 🌟 Best Practices

1. **Performance**
   - Optimize images before adding
   - Minimize custom CSS/JS
   - Use CSS variables for theming

2. **Accessibility**
   - Use semantic HTML
   - Add alt text to images
   - Ensure keyboard navigation works
   - Maintain good color contrast

3. **Responsiveness**
   - Test on mobile devices
   - Use flexible layouts
   - Check at different screen sizes

4. **SEO**
   - Update meta descriptions
   - Use proper heading hierarchy
   - Add descriptive link text

## 📱 Responsive Design

The website is fully responsive and tested on:

- ✅ Desktop (1920px+)
- ✅ Laptop (1024px - 1919px)
- ✅ Tablet (768px - 1023px)
- ✅ Mobile (320px - 767px)

Breakpoints are defined in the CSS media queries.

## 🔗 Useful Links

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)
- [Liquid Template Language](https://shopify.github.io/liquid/)

## 📄 License

This website is part of the Earning Robot project and is released under the MIT License.

## 🤝 Contributing

To contribute to the website:

1. Fork the repository
2. Create a feature branch
3. Make your changes in the `website/` directory
4. Test locally with Jekyll
5. Submit a pull request

## 💡 Tips

- The demo is purely client-side JavaScript (no backend needed)
- All animations use CSS for better performance
- The site is static - no server-side processing required
- Perfect for GitHub Pages hosting

---

**Built with ❤️ for showcasing autonomous earning**
