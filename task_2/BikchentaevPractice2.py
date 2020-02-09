import my_modules.irhelper as irh

helper = irh.IRHelper(r'D:\PyCharmWorkspace\InfoRetrival\data\books\midtxt')

# _, matrix = helper.build_incidence_matrix(True, 'my_incidence_matrix')
# print(matrix.describe())
# print(matrix)
# print(matrix.index.values[9])

file_map, index = helper.build_inverted_index(True, "my_inverted_index")
print(len(index.keys()))
print(file_map)

# print(helper.bool_search('(Battle-ax AND Battle-field) AND NOT BATTLE-GROUND',
#                          'my_inverted_index.json', 'file_map.json'))
