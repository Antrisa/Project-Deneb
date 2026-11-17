extends RefCounted
# Low modular terrace trim. Open ends align with library, shop and promenade approaches.
static func paint(n: Node2D) -> void:
	var runs: Array = [
		[Vector2(99,72),Vector2(101,70)],
		[Vector2(104,70),Vector2(110,70),Vector2(110,81),Vector2(108,83)],
		[Vector2(105,80),Vector2(101,76)],
		[Vector2(118,112),Vector2(120,110),Vector2(125,110),Vector2(130,115),Vector2(130,119),Vector2(129,119)],
		[Vector2(125,119),Vector2(120,119),Vector2(118,117)]
	]
	for run in runs:
		for i in range(run.size()-1):piece(n,run[i]*16.0,run[i+1]*16.0)
static func piece(n: Node2D,a: Vector2,b: Vector2) -> void:
	n.draw_line(a+Vector2(1,4),b+Vector2(1,4),Color(0.08,0.12,0.17,0.27),9)
	n.draw_line(a+Vector2(0,2),b+Vector2(0,2),Color("5d6972"),7)
	n.draw_line(a,b,Color("aaa99c"),7)
	n.draw_line(a+Vector2(0,-1),b+Vector2(0,-1),Color("d4cbb6"),4)
	n.draw_line(a+Vector2(0,-3),b+Vector2(0,-3),Color("eee2c8"),1)
	var tangent: Vector2=(b-a).normalized()
	var normal:=Vector2(-tangent.y,tangent.x)
	for d in range(0,int(a.distance_to(b)),16):
		var center:=a+tangent*d
		n.draw_line(center-normal*2,center+normal*2,Color("858b87"),1)
	# Small end caps communicate real curb pieces, not a painted border line.
	for end in [a,b]:
		n.draw_rect(Rect2(end-Vector2(3,3),Vector2(6,6)),Color("b7b9ad"))
		n.draw_line(end-Vector2(2,2),end+Vector2(2,-2),Color("eee2c8"),1)
