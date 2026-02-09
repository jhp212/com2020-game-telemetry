with open("game/Godot/Singleton/game_data.gd") as game_data:
    data = list(map(lambda line: line.removesuffix("\n"), game_data.readlines()))
    game_data.close()

tower_data_start: int = data.index("var tower_data = {")
potentialtowerdict = ''.join(map(lambda line: line.lstrip("\t"),data[tower_data_start+1:]))
stack = ["{"]
for index,char in enumerate(potentialtowerdict):
    if char in ['{', '[', '(','"']:
        if char == '"' and stack[-1] == '"':
            stack.pop()
        else:
            stack.append(char)
    elif char in ['}',']',')','"']:
        if  ['{', '[', '(','"'].index(stack[-1]) == ['}',']',')','"'].index(char):
            stack.pop()
    if len(stack) == 0:
        tower_data = eval("{"+potentialtowerdict[:index+1])
        break
if __name__ == "__main__":
    print(tower_data)

del tower_data_start, potentialtowerdict, stack

enemy_data_start: int = data.index("var enemy_data = {")
potentialenemydict = ''.join(map(lambda line: line.lstrip("\t"),data[enemy_data_start+1:]))
stack = ["{"]
for index,char in enumerate(potentialenemydict):
    if char in ['{', '[', '(','"']:
        if char == '"' and stack[-1] == '"':
            stack.pop()
        else:
            stack.append(char)
    elif char in ['}',']',')','"']:
        if  ['{', '[', '(','"'].index(stack[-1]) == ['}',']',')','"'].index(char):
            stack.pop()
    if len(stack) == 0:
        enemy_data = eval("{"+potentialenemydict[:index+1])
        break
if __name__ == "__main__":
    print(enemy_data)

del enemy_data_start, potentialenemydict, stack