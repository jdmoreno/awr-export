from pathlib import Path, WindowsPath

def main():
    file_str = "C:/2.documents/rmg/Projects/EPS.Platform/Platform.Projects/2023.Active.Space.decommision/parallel/PPD/*.html"
    file_path = Path(file_str)
    parent_path = file_path.parent

    print(f"path: {file_path} - \nparent: {parent_path}")

    print(f"path: {file_path.iterdir()}")
    for child in file_path.iterdir(): child

    # for root, dirs, files in parent_path.walk(on_error=print):
    #     print(
    #         root,
    #         "consumes",
    #         sum((root / file).stat().st_size for file in files),
    #         "bytes in",
    #         len(files),
    #         "non-directory files"
    #     )

    return


if __name__ == '__main__':
    main()
