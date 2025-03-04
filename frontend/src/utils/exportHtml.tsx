interface PageData {
    nodes: Record<
        string,
        {
            type?: { resolvedName?: string }
            data?: {
                type?: { resolvedName?: string }
                name?: string
            }
            props?: Record<string, any>
            nodes?: string[]
        }
    >
    ROOT?: string
    rootNodeId?: string
}

interface BookData {
    pages?: Record<string, PageData>
}

export const exportHtml = (bookData: BookData): string => {
    // Create basic HTML template
    const pageContents = Object.entries(bookData.pages || {})
        .map(([pageNum, pageData]: [string, PageData]) => {
            // Process Craft.js JSON to HTML
            let pageHtml = ""

            try {
                console.log("Page data:", typeof pageData.nodes)
                // Convert the node structure to HTML
                if (pageData && pageData.nodes) {
                    const rootNodeId = pageData.ROOT || pageData.rootNodeId || Object.keys(pageData.nodes)[0]
                    pageHtml = convertNodeToHtml(rootNodeId, pageData.nodes)
                }
            } catch (err) {
                console.error("Error converting page to HTML:", err)
                console.error("Page data:", pageData)
                pageHtml = `<p>Error rendering page ${pageNum}</p>`
            }

            return `
      <div class="book-page" id="page-${pageNum}">
        <div class="page-content">
          ${pageHtml}
        </div>
        <div class="page-footer">
          <span class="page-number">${pageNum}</span>
        </div>
      </div>
    `
        })
        .join("\n")

    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Book Export</title>
      <style>
        body {
          font-family: 'Georgia', serif;
          line-height: 1.6;
          margin: 0;
          padding: 0;
          background-color: #f9f9f9;
        }
        .book-page {
          width: 21cm;
          min-height: 29.7cm;
          padding: 2cm;
          margin: 1cm auto;
          background-color: white;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
          position: relative;
          page-break-after: always;
        }
        .page-content {
          height: 25.7cm;
          overflow: hidden;
          position: relative;
        }
        .page-footer {
          position: absolute;
          bottom: 1cm;
          width: calc(100% - 4cm);
          text-align: center;
          font-size: 12px;
          color: #666;
        }
        h1, h2, h3, h4, h5, h6 {
          margin-top: 0;
          line-height: 1.2;
        }
        img {
          max-width: 100%;
          height: auto;
        }
        @media print {
          .book-page {
            margin: 0;
            box-shadow: none;
          }
        }
        .clearfix:after {
          content: "";
          display: table;
          clear: both;
        }
      </style>
    </head>
    <body>
      ${pageContents}
    </body>
    </html>
  `
}

// Helper function to convert a Craft.js node to HTML
const convertNodeToHtml = (nodeId: string, nodes: Record<string, any>): string => {
    const node = nodes[nodeId]
    if (!node) return ""

    // Extract component type and props
    const { type, props = {}, nodes: childNodeIds = [], data } = node

    // Use resolved name from either location
    const componentType = type?.resolvedName || data?.type?.resolvedName || data?.name

    // Process children first
    const childrenHtml = Array.isArray(childNodeIds)
        ? childNodeIds.map((childId) => convertNodeToHtml(childId, nodes)).join("")
        : ""

    // Generate HTML based on component type
    switch (componentType) {
        case "Text":
            return `<p style="font-size: ${props.fontSize || 16}px; text-align: ${props.textAlign || "left"}">${
                props.text || ""
            }</p>`

        case "Heading":
            const headingLevel = props.variant?.substring(1) || "2"
            return `<h${headingLevel} style="text-align: ${props.textAlign || "left"}">${
                props.text || ""
            }</h${headingLevel}>`

        case "Image":
            return `<img src="${props.src || ""}" alt="${props.alt || ""}" style="width: ${props.width || 100}%" />`

        case "Container":
            // Handle different positioning types
            let styles = `padding: ${props.padding || 20}px; background: ${props.background || "transparent"};`

            if (props.position === "absolute") {
                styles += ` position: absolute; left: ${props.left || 0}; top: ${props.top || 0}; width: ${
                    props.width || "100%"
                };`
            } else {
                // Handle float for side-by-side positioning
                if (props.float === "left" || props.float === "right") {
                    styles += ` float: ${props.float}; width: ${props.width || "100%"};`
                    return `<div style="${styles}">${childrenHtml}</div>`
                } else {
                    styles += ` width: ${props.width || "100%"};`
                    return `<div style="${styles}" class="clearfix">${childrenHtml}</div>`
                }
            }

            return `<div style="${styles}">${childrenHtml}</div>`

        default:
            // Try to infer element type from presence of children
            if (childrenHtml) {
                return `<div>${childrenHtml}</div>`
            }
            return ""
    }
}
