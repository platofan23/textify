export const exportToHtml = (pages: any[]): string => {
    // Create HTML content for each page
    const pagesHtml = pages
        .map((page) => {
            // Get HTML content from the page
            const pageContent = page.content && page.content.html ? page.content.html : "<p>No content</p>"

            // Generate HTML for this page
            return `
      <div class="book-page">
        <h2>${page.title}</h2>
        <div class="page-content">
          ${pageContent}
        </div>
      </div>
    `
        })
        .join("\n")

    // Generate complete HTML document
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Book Export</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .book-page {
      margin-bottom: 40px;
      page-break-after: always;
      border: 1px solid #eee;
      padding: 20px;
      border-radius: 5px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    h1, h2 {
      color: #2c3e50;
    }
    img {
      max-width: 100%;
      height: auto;
    }
    @media print {
      .book-page {
        border: none;
        box-shadow: none;
      }
    }
  </style>
</head>
<body>
  <h1>Book Export</h1>
  ${pagesHtml}
</body>
</html>
  `

    return html
}
