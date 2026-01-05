from functions.get_file_content import get_file_content

from config import MAX_CHARS


def run_tests():
    # 1. Truncation test
    print('get_file_content("calculator", "lorem.txt"):')
    content = get_file_content("calculator", "lorem.txt")

    if content.startswith("Error:"):
        print(content)
    else:
        print("Result:")
        print(f"  Content length: {len(content)}")
        print(
            "  Truncation message present:",
            content.endswith(
                f'[...File "lorem.txt" truncated at {MAX_CHARS} characters]'
            ),
        )
    print()

    # 2. Read main.py
    print('get_file_content("calculator", "main.py"):')
    print(get_file_content("calculator", "main.py"))
    print()

    # 3. Read pkg/calculator.py
    print('get_file_content("calculator", "pkg/calculator.py"):')
    print(get_file_content("calculator", "pkg/calculator.py"))
    print()

    # 4. Attempt to read outside working directory
    print('get_file_content("calculator", "/bin/cat"):')
    print(get_file_content("calculator", "/bin/cat"))
    print()

    # 5. Attempt to read non-existent file
    print('get_file_content("calculator", "pkg/does_not_exist.py"):')
    print(get_file_content("calculator", "pkg/does_not_exist.py"))


if __name__ == "__main__":
    run_tests()
