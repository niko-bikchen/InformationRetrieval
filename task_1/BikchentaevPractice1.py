import os
import re
import io


# Returns a list of absolute paths of the
# files from the specified directory
# ! You should specify a full path to the directory
# ! as it will form a part of the absolute path of a file
def files_in_dir(dir_path: str):
    return [fr'{dir_path}\\{item}' for item in os.listdir(fr'{dir_path}') if item.endswith('.txt')]


files = files_in_dir(r'D:\PyCharmWorkspace\InfoRetrival\data\books\bigtxt')
collection_size = 0
words_in_collection = 0
lexicon = []

# Open each file from the list of files
# and save words from it to the lexicon
for file in files:
    collection_size += os.stat(file).st_size
    with io.open(fr'{file}', encoding='utf_8') as file_handler:
        for line in file_handler:
            for word in line.split():
                words_in_collection += 1
                res = re.match(r"[a-z]+['-]?[a-z]+", word.lower())
                if res is not None:
                    lexicon.append(res.group())
    lexicon = list(set(lexicon))  # remove duplicates from the lexicon

lexicon = sorted(lexicon)  # sort the lexicon alphabetically

# Write lexicon to the file
with open('lexicon.txt', 'w') as file:
    file.write('\n'.join(lexicon))

print(f"Size of the collection: {collection_size / 1000} KB")
print("Number of words in the collection: ", words_in_collection)
print(f"Size of the lexicon: {os.stat('lexicon.txt').st_size / 1000} KB")
print("Number of words in the lexicon: ", len(lexicon))
