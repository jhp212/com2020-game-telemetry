class PackedVector2Array:
    def __init__(self, *x) -> None:
        if len(x) % 2 == 1:
            raise ValueError("Vector2Array should be a list of Vector2")
        self.values = x
    
    def toList(self) -> list:
        output = list()
        for ind in range(0, len(self.values),2):
            output.append((self.values[ind],self.values[ind+1]))
        return output

def path_interpreter(level_name: str):
    with open('game/Godot/Scenes/Maps/'+level_name+".tscn") as map_file:
        map_file_data = list(map(lambda line: line.removesuffix("\n"),map_file.readlines()))
        map_file.close()
    path_data_index = 0
    for index,data in enumerate(map_file_data):
        if '[sub_resource type="Curve2D"' in data:
            path_data_index = index
            break
    potential_path_slice = map_file_data[path_data_index:]
    empty_index = potential_path_slice.index('')
    pathdata = eval(''.join(potential_path_slice[1:4]).removeprefix("_data = "))
    # Data, when saved as the 2d vector array, is saved as "(IN), (OUT), (POINT) triples".
    # This means that every 3rd point is the "on-curve point"
    points = pathdata['points'].toList()[2::3]
    delta = lambda start, end: tuple(map(lambda a, b: b-a, start, end))
    vectabs = lambda point: sum(map(lambda x: x**2, point))**0.5
    distances = [vectabs(delta(points_i,points_idx)) for points_i, points_idx in zip(points[0:len(points)-1],points[1:len(points)])]
    def calculatePosition(distance) -> tuple[int, ...]:
        if 0>distance or distance > sum(distances):
            return (0,0)
        totaldist = 0
        index = -1
        for i, stored_dist in enumerate(distances):
            totaldist += stored_dist
            if totaldist >= distance:
                index = i
                break
        pointa = points[index]
        pointb = points[index+1]
        len_along = distance - (totaldist - distances[index])
        ratio_along = len_along/distances[index]
        result = tuple(map(lambda a,b: int(round(a+b,0)), map(lambda x: ratio_along*x,pointb),map(lambda x: (1-ratio_along)*x,pointa)))
        return result
    return sum(distances), calculatePosition
if __name__ == "__main__":
    length, path1 = path_interpreter('map_1')
    print(f'length: {length}')
    for i in range(100):
        t = i*length/100
        print(f'{int(round(t))}: {path1(t)}')