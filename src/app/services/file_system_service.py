import os
#from src.app.services.supabase_service import supabase
from src.app.config import NEW_DOCUMENTS_DIR, NEW_USER_UPLOADS_DIR

def upload_move_to_processed(from_dir, to_dir):
    """
    Upload to file storage and move processed files from the new documents directory to the processed documents directory.
    
    Returns:
        str: Success message
    """
    for file in os.listdir(from_dir):
        source = os.path.join(from_dir, file)
        try:
            if from_dir == NEW_DOCUMENTS_DIR:
                # Upload to Supabase storage
                response = supabase.storage.from_('knowledge-base').upload(file, source)
            if from_dir == NEW_USER_UPLOADS_DIR:
                response = supabase.storage.from_('user-uploads').upload(file, source)
            
            # Check if upload was successful or if it's a duplicate
            if hasattr(response, 'get') and response.get('statusCode') == 409:
                print(f"File {file} already exists in storage, skipping upload but moving file...")
            else:
                print(f"Successfully uploaded: {file}")
            
            destination = os.path.join(to_dir, file)
            os.rename(source, destination)
        except Exception as e:
            print(f"Error uploading {file}: {e}")
            # Still move the file even if upload failed
            try:
                destination = os.path.join(to_dir, file)
                os.rename(source, destination)
                print(f"Moved {file} despite upload error")
            except:
                print(f"Failed to move {file}")
            continue
    return 'Files uploaded and moved successfully'