import os


# Initialize OpenAI embeddings through Langchain
def find_in_files(directory, extension):
    # Create a list to store the paths of .md files
    md_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Find all .md files in the current directory
        for file in files:
            if file.endswith(extension):
                md_files.append(os.path.join(root, file))

    # Return the list of .md files
    return md_files