Upload Documents to Storage
===

# Table of Contents

- [Adding new documents to the Knowledge Bank](#adding-new-documents-to-the-knowledge-bank)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)


# Introduction

This document provides a guide for adding new documents to the Knowledge Bank of VINO AI. The process has changed with the new file structure and processing pipeline. Follow these instructions to ensure documents are correctly uploaded to both the RAG (ChromaDB) and SQL (Supabase) backends.

**Note:** User documents uploaded through the application are processed and stored in both ChromaDB and Supabase automatically. PDF documents are chunked using a simplified process.

# Document Requirements

- **Preferred file extension**: `.md` ([why?](#why-markdown))
  * Also supported: `.txt`, `.pdf`, `.docx`
- **No need for Table of Contents**: ToC is created automatically during processing.
- **Section Limit**: Sections under 300 tokens are processed as a whole; larger sections are further chunked.
- **Required Folders**: Ensure `data/kb_new/` exists for new uploads. Processed files will be moved to `data/kb/`.
- **No Duplicates**: Duplicate filenames are not allowed and will cause an error.

## Document Structure

The document should follow this structure:

**Required Elements:**
- **Title**: Clear, descriptive heading with `===` underline.
- **Summary Section**: Brief overview (recommended as first section).
- **Main Content**: Use H1, H2, and H3 headings for organization.
- **Practical Examples**: Include "Application Examples" or similar sections.
- **Step-by-Step Guides**: For procedures, provide numbered steps.
- **Considerations/Limitations**: Note potential issues or important notes.
- **Resource Links**: External references and further reading.

## Content Guidelines
- Use descriptive section headings (avoid generic titles).
- Include practical examples.
- Structure for scannability: bullet points, numbered lists, clear hierarchies.
- Define key terms (bold on first use).
- Cross-reference related documents when relevant.

## Quality Checklist

Before processing any document, verify:
- [ ] Clear, descriptive title with proper H1 formatting
- [ ] No manual TOC markers
- [ ] Summary section included
- [ ] All technical terms defined on first use
- [ ] "Actionable for students:" sections included
- [ ] Real-world examples relevant to student projects
- [ ] Considerations/limitations section present
- [ ] Resource links functional and relevant
- [ ] Consistent formatting throughout

## Why Markdown?

- Lightweight and readable
- Universal compatibility
- Version control friendly
- Structured data extraction
- AI-friendly format
- Future-proof
- Rich formatting support
- Fast processing
- Search optimization

# Document Processing Steps

Before you start, make sure your Supabase project is set up. You can find the setup instructions in the [Supabase Setup Guide](supabase-setup.md).

## Step-by-Step Guide for Adding Documents

1. **Create the Document**:
   - Save the file with a `.md` extension in the `data/kb_new/` directory
   - Use a descriptive filename (e.g., `ProjectManagement.md`)

2. **Structure Your Content**:
   - Start with a clear H1 title using `===` underline
   - Include all required sections from the template
   - Use an existing document in `data/kb/` as a structural reference if needed

3. **Quality Review**:
   - Verify all sections have descriptive headings
   - Check that "Actionable for students:" items are included where relevant
   - Ensure examples are student-project focused
   - Have another team member review before processing

4. **Processing & Upload**:
   - Run the following command in the project root:
     ```
     uv run python -m file_upload.file_processor --default
     ```
   - The script will process all new documents in `data/kb_new/` and upload them to both ChromaDB and Supabase
   - Processed files will be moved to `data/kb/`
   - Check the terminal output for upload status and errors
   - Document any processing errors for troubleshooting

## File Organization
- **Location**: All new KB documents go in `data/kb_new/` and are moved to `data/kb/` after processing
- **Naming**: Use PascalCase for filenames (e.g., `SoftwareTesting.md`)

## Check Upload

To verify that documents were correctly uploaded:

- **ChromaDB**:
  1. Check the terminal output after running the processor for a summary of uploaded documents.


- **Supabase**:
  1. Log in to https://supabase.com and access your project.
  2. In the `Table Editor`, check the `filemetadata` and `largeobject` tables for new entries.
  3. In the `Storage` section, verify documents in the `knowledge-base` bucket.

If you encounter issues, review the terminal output and logs, and consult the development team for troubleshooting.