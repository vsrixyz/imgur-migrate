from re import findall, escape, sub
from requests import get as r_get
from os.path import join, exists, relpath
from os import walk, makedirs
from argparse import ArgumentParser

available_modes = {"wikilink", "mdlink"}
available_modes_text = " or ".join(available_modes)

def find_all_imgur_links(text: str) -> list[tuple[str, str, str]]:
    """
    Find all embedded Imgur links in the file like ![text]()\n
    Only match links that start with https://i.imgur.com/\n
    Return a list of tuples, where each tuple is ("<text>", "https://i.imgur.com/<code>", ".<extension>")
    """
    imgur_pattern = r'!\[(.*?)\]\((https:\/\/i\.imgur\.com\/\w+)(\.\w+)?\)'

    imgur_links = findall(imgur_pattern, text)
    return imgur_links

def replace_external_url_link_with_internal_link(url: str, path: str, text: str, mode: str = "wikilink", alt_text: str = "") -> str:
    """replace ![](<imgur link>) with the ![[<local image path>]]"""
    if path.startswith("http"):
        raise ValueError("should be a local path")
    
    # match "![text](path)" and "![](path)"
    pattern = r"!\[([^\]]*)\]\((url)\)|!\[\]\((url)\)"
    escaped_url = escape(url)
    pattern = pattern.replace("url", escaped_url)
    if mode == "wikilink":
        target = f"![[{path}]]"
    elif mode == "mdlink":
        target = f"![{alt_text}]({path})"
    else:
        raise ValueError(f"mode should be {available_modes_text}")
    replaced_text = sub(pattern, target, text)
        
    return replaced_text

def dir_imgur_migrate(working_dir: str, mode: str = "wikilink", images_dir: str = "") -> None:
    """go over every file in the directory recursively"""
    print(f"About to process all .md files under {working_dir}")
    output_dir = ""
    if images_dir:
        output_dir = join(working_dir, images_dir)
        makedirs(output_dir, exist_ok=True)
    for root, _, files in walk(working_dir):
        for file in files:
            if file.endswith(".md"):
                file_imgur_migrate(root, file, mode, output_dir)
    print("All done!")

def file_imgur_migrate(working_dir: str, filename: str, mode: str = "wikilink", output_dir: str = "") -> None:
    if not filename.endswith(".md"):
        print(f"Skipping {filename} because it's not a .md file")
        return
    file_path = join(working_dir, filename)
    print(f"Processing {file_path}...")

    with open(file_path, "r") as file:
        text = file.read()

    imgur_links = find_all_imgur_links(text)
    print(f"Found {len(imgur_links)} imgur links in {file_path}")
    if len(imgur_links) == 0:
        return
    
    # Download each image to the current directory
    print("Downloading images from imgur...")
    downloaded_count = 0
    for i, link in enumerate(imgur_links):
        alt_text, link_base, link_ext = link
        url = link_base + link_ext
        try:
            response = r_get(url, timeout=20, headers={"User-Agent": "imgur-migrate/1.0"})
        except Exception as err:
            print(f"Skipping {url}: request failed ({err})")
            continue

        if response.status_code != 200:
            print(f"Skipping {url}: HTTP {response.status_code}")
            continue

        content_type = response.headers.get("Content-Type", "")
        if len(response.content) == 0:
            print(f"Skipping {url}: empty response body")
            continue

        if content_type.startswith("text/"):
            print(f"Skipping {url}: non-image content type ({content_type})")
            continue
        
        # use a snake-case file name
        safe_filename = filename.replace('.md', '').lower().replace(' ', '-')
        ind = i + 1
        image_name = f'{safe_filename}-{ind}{link_ext}'
        image_dir = output_dir if output_dir else working_dir
        image_path = join(image_dir, image_name)
        
        # check if the image already exists
        while exists(image_path):
            ind += 1
            image_name = f'{safe_filename}-{ind}{link_ext}'
            image_path = join(image_dir, image_name)

        link_path = image_name
        if output_dir:
            link_prefix = relpath(output_dir, start=working_dir).replace("\\", "/")
            link_path = f"{link_prefix}/{image_name}"

        replaced_text = replace_external_url_link_with_internal_link(url, link_path, text, mode=mode, alt_text=alt_text)
        
        # don't save image if no links are replaced
        if text == replaced_text:
            continue
        
        # save image
        text = replaced_text
        with open(image_path, 'wb') as f:
            f.write(response.content)
        downloaded_count += 1
        
    print(f"Downloaded {downloaded_count} image(s) to {working_dir}")
        
    # Write the modified text back to the file
    if downloaded_count == 0:
        print("No valid images were downloaded. File was not changed.")
        return

    print("Replacing links...")
    with open(file_path, "w") as file:
        file.write(text)
    print("Done!")
    
def main():
    parser = ArgumentParser()
    parser.add_argument('directory', nargs='?', default=".", help='directory to process, default to current directory')
    parser.add_argument('filename', nargs='?', help='file name')
    parser.add_argument('--mode', '-m', nargs='?', default="wikilink", help='wikilink or mdlink')
    parser.add_argument('--images-dir', nargs='?', default="", help='store downloaded images in a subdirectory under <directory>')
    args, _ = parser.parse_known_args()
    
    working_dir = args.directory
    filename = args.filename
    mode = args.mode
    images_dir = args.images_dir
    if mode not in available_modes:
        print(f"Error: mode should be {available_modes_text}")
        return
    
    # if no filename given
    if not filename:
        dir_imgur_migrate(working_dir, mode, images_dir)
    else:
        output_dir = join(working_dir, images_dir) if images_dir else ""
        if output_dir:
            makedirs(output_dir, exist_ok=True)
        file_imgur_migrate(working_dir, filename, mode=mode, output_dir=output_dir)

if __name__ == "__main__":
    main()