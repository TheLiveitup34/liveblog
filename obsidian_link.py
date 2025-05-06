import os 
import re
import hashlib
from datetime import date

def convert_to_hugo_format(obsidian_app_directory, post_path_file, post_file, modified=False):

    if modified==True:
        old_index_file_contents = ""
        # open the index.md file and read the contents  
        with open(os.path.join(obsidian_app_directory, post_file), "r", encoding="utf-8") as f:

            old_index_file_contents = f.read()
        # close the index.md file

    index_file = os.path.join(post_path_file, "index.md")
    with open(os.path.join(obsidian_app_directory, post_file), "r", encoding="utf-8") as f:
                contents = f.read()
                # write the contents to the index.md file
                with open(index_file, "w", encoding="utf-8") as f2:
                    # loop through the contets of the obsidian file and copy the images over to the post path directory
                    # generate a hash file in the post path with version.hash
                    hash_file = os.path.join(post_path_file, "version.hash")
                    # generate a 256 bit hash of the contents of the obsidian file
                    hash_object = hashlib.sha256(contents.encode())
                    # get the hash in hex format
                    hex_dig = hash_object.hexdigest()
                    # write the hash to the hash file
                    with open(hash_file, "w") as f3:
                        f3.write(hex_dig)
                        
                    first_image_found = False
                    first_image_name = ""
                    for line in contents.splitlines():
                        # check if the line contains a link to an image
                        if re.search(r"!\[\[.*\]\]", line):
                            # get the image name from the line
                            image_name = re.search(r"!\[\[(.*)\]\]", line).group(1)
                            if not first_image_found:
                                first_image_found = True
                                first_image_name = image_name
                            # check if the image exists in the obsidian app directory
                            if os.path.exists(os.path.join(obsidian_app_directory, image_name)):
                                # copy the image to the post path directory
                                with open(os.path.join(obsidian_app_directory, image_name), "rb") as f3:
                                    with open(os.path.join(post_path_file, image_name), "wb") as f4:
                                        f4.write(f3.read())

                    # replace the image: cover.jpg with the first image name found in the obsidian file
                    if first_image_found:
                        contents = re.sub(r"image: cover.jpg", f"image: {first_image_name}", contents)
                        # remove the first image markdown with the first image name found in the obsidian file
                        contents = re.sub(r"!\[\["+first_image_name+"\]\]", "", contents)
                    else:
                        # remove the image: cover.jpg line from the contents
                        contents = re.sub(r"image: cover.jpg", "", contents)
                    # write the contents to the index.md file
                    date_today = date.today()
                    date_string = date_today.strftime("%Y-%m-%d")
                    if modified == False:
                        # update the date: to current date in YYYY-MM-DD format
                        contents = re.sub(r"date: .*", f"date: " + date_string, contents)
                    else: 
                        old_date = re.search(r"date: (.*)", old_index_file_contents).group(1)
                        contents = re.sub(r"date: .*", f"date: " + old_date, contents)
                    new_contents = []
                    # loop through the contents one by one and write to the index.md file
                    i = 0
                    header_line_found = 0
                    for line in contents.splitlines():
                        # check if the line contains a link to an image
                        
                        # check if the line contains toc: "False"
                        if re.search(r"toc: .*", line):
                            # remove the toc: "False" line from the contents
                            line = re.sub(r"toc: .*", "toc: false", line)


                        if (header_line_found == 2 and modified == True):
                            # get the date from the old index file contents
                            old_date = re.search(r"date: (.*)", old_index_file_contents).group(1)
                            # check if the date is different from the current date
                            if old_date != date_string:
                                # insert a line into the new_contents list
                                new_contents.insert(i, f"#### Last modified: {date_today.strftime('%b %d, %Y')}")
                                i += 1
                            header_line_found = 0
                        if re.search(r"^---", line):
                            header_line_found += 1
                        if re.search(r"!\[\[.*\]\]", line):
                            # get the image name from the line
                            # modify the image line to ![Title](image_name)
                            image_name = re.search(r"!\[\[(.*)\]\]", line).group(1)
                            # get the title from the line bfore current line
                            # remove the content of the line before the image line
                            line = re.sub(r"!\[\[(.*)\]\]", f"![]({image_name})", line)
                        # append the line to the new contents
                        new_contents.append(line)
                        i += 1
                    f2.write("\n".join(new_contents))

                    print(f"Created {index_file} from {post_file}")

def main():

    # get the current directory
    current_directory = os.getcwd()
    # get the post path directory
    post_path = os.path.join(current_directory,"content", "post")

    # get the obsidian app directory from the users documents folder
    obsidian_app_directory = os.path.join(os.path.expanduser("~"), "Documents", "Obsidian Vault", "posts") + os.sep
    # check if the obsidian app directory exists
    if not os.path.exists(obsidian_app_directory):
        print("Obsidian app directory does not exist")
        return
    
    # get the list of the .md files in the post path directory
    post_files = [f for f in os.listdir(obsidian_app_directory) if f.endswith(".md")]
    # loop through the post files and check if a directory exists in the post path directory
    for post_file in post_files:
        post_name = os.path.splitext(post_file)[0]
        # remove the .md and replace spaces with dashes
        post_name = post_name.replace(" ", "-")
        # convert to lowercase
        post_name = post_name.lower()
        # check if the post name exists in the post path directory
        post_path_file = os.path.join(post_path, post_name)

        # if the path folder dosent exist then create a folder then a index.md file and copy the contents of the obsidian file to the index.md file
        if not os.path.exists(post_path_file):
            os.makedirs(post_path_file)
            # create the index.md file
            convert_to_hugo_format(obsidian_app_directory, post_path_file, post_file)
            # open the obsidian file and read the contents
            
        else:
            # get the version.hash file in the post path directory
            hash_file = os.path.join(post_path_file, "version.hash")
            # check if the hash file exists
            if os.path.exists(hash_file):
                # read the hash file and get the hash value
                with open(hash_file, "r") as f:
                    hash_value = f.read()
                # get the contents of the obsidian file
                with open(os.path.join(obsidian_app_directory, post_file), "r", encoding="utf-8") as f:
                    contents = f.read()
                    # generate a 256 bit hash of the contents of the obsidian file
                    hash_object = hashlib.sha256(contents.encode())
                    # get the hash in hex format
                    hex_dig = hash_object.hexdigest()
                    # check if the hash value is different from the current hash value
                    if hex_dig != hash_value:
                        # update the index.md file with the new contents
                        convert_to_hugo_format(obsidian_app_directory, post_path_file, post_file, True)

    # send command of hugo server to run the hugo server to allow the user to see the changes in the browser
    os.system('start http://localhost:1313/')
    os.system("hugo server")



if __name__ == "__main__":
    main()