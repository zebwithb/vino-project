Supabase Project Setup
===

# Table of Contents
- [Supabase Project Setup](#supabase-project-setup)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Supabase Project Setup](#supabase-project-setup-1)
- [Conclusion](#conclusion)

# Introduction

This document outlines the steps to set up a Supabase project for file uploads and processing. Follow these instructions to ensure your project is ready for document management.

Supabase is used for persistent storage of documents and metadata and their retrieval.

# Supabase Project Setup

1. Log in to your Supabase account at [Supabase.com](https://supabase.com).
2. Create a new project by clicking on "New Project" and filling in the required details
3. Once the project is created, navigate to the "SQL Editor" section.
4. Paste the following SQL commands to create the necessary tables and storage bucket:

```sql

-- Create the largeobject table
CREATE TABLE public.largeobject (
  oid bigint NOT NULL DEFAULT nextval('largeobject_oid_seq'::regclass),
  plain_text text NULL,
  CONSTRAINT largeobject_pkey PRIMARY KEY (oid)
) TABLESPACE pg_default;

-- Create the filemetadata table
CREATE TABLE public.filemetadata (
  id bigint NOT NULL DEFAULT nextval('filemetadata_id_seq'::regclass),
  file_name text NULL,
  file_size bigint NULL,
  file_type text NULL,
  page_count smallint NULL,
  word_count integer NULL,
  char_count integer NULL,
  keywords text[] NULL,
  source text NULL,
  abstract text NULL,
  large_object_oid bigint NULL,
  CONSTRAINT filemetadata_pkey PRIMARY KEY (id),
  CONSTRAINT fk_large_object FOREIGN KEY (large_object_oid) REFERENCES largeobject(oid) ON UPDATE CASCADE ON DELETE CASCADE
) TABLESPACE pg_default;

```
5. Execute the SQL commands to create the tables.
6. Next, create a storage bucket for your documents:
   - Navigate to the "Storage" section in Supabase.
   - Click on "New Bucket" and name it `knowledge-base`.
7. Create another bucket named `user-uploads` for user-uploaded files.
8. In the "Settings" find your Project ID and API keys. You will need these for your application configuration.
9. In the root folder of your project, create a `.env` file and add the following environment variables:

```plaintext
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
``` 
Replace `your_supabase_url` and `your_supabase_key` with the values from your Supabase project settings.
10. Save the `.env` file and ensure it is included in your `.gitignore` to keep your credentials secure.

# Conclusion

Your Supabase project is now set up and ready for file uploads and processing. You can proceed with the document management tasks as outlined in the [Document Processing Guide](upload-docs.md). If you encounter any issues, refer to the Supabase documentation or seek assistance from the developers.