extends CanvasLayer
# A short playable community-table game; no inventory or quest effects.
var open:=false
var cells: Array[int]=[]
var outcome:="Your turn — make a line of three."
var panel: Control
var buttons: Array[Button]=[]
var status: Label
func _ready() -> void:
	layer=18
	panel=Panel.new();panel.position=Vector2(70,12);panel.size=Vector2(180,156);add_child(panel)
	var title:=Label.new();title.text="Community table • Three in a row";title.position=Vector2(6,4);title.add_theme_font_size_override("font_size",9);panel.add_child(title)
	for i in range(9):
		var b:=Button.new();b.position=Vector2(36+(i%3)*36,22+(i/3)*30);b.size=Vector2(32,28)
		b.pressed.connect(_move.bind(i));panel.add_child(b);buttons.append(b)
	status=Label.new();status.position=Vector2(6,116);status.size=Vector2(170,16);status.add_theme_font_size_override("font_size",8);panel.add_child(status)
	var again:=Button.new();again.text="Again";again.position=Vector2(12,133);again.size=Vector2(70,19);again.pressed.connect(start);panel.add_child(again)
	var close:=Button.new();close.text="Leave";close.position=Vector2(96,133);close.size=Vector2(70,19);close.pressed.connect(hide_game);panel.add_child(close)
	panel.hide()
func start() -> void:
	open=true;panel.show();cells.assign([0,0,0,0,0,0,0,0,0]);outcome="Your turn — make a line of three.";_refresh()
func hide_game() -> void:
	open=false;panel.hide()
func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("cancel"):hide_game()
func winner(board: Array[int]) -> int:
	for line in [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]:
		if board[line[0]]!=0 and board[line[0]]==board[line[1]] and board[line[1]]==board[line[2]]:return board[line[0]]
	return 0
func _move(i: int) -> void:
	if cells[i]!=0 or winner(cells)!=0 or not cells.has(0):return
	cells[i]=1
	if winner(cells)==0 and cells.has(0):
		var pick:=-1
		# Win if possible, otherwise block, then choose a strategic open square.
		for mark in [2,1]:
			for j in range(9):
				if cells[j]!=0:continue
				var trial: Array[int]=cells.duplicate();trial[j]=mark
				if winner(trial)==mark:pick=j;break
			if pick>=0:break
		if pick<0:
			for j in [4,0,2,6,8,1,3,5,7]:
				if cells[j]==0:pick=j;break
		cells[pick]=2
	var win:=winner(cells)
	outcome="You win!" if win==1 else "The table wins. Try another round?" if win==2 else "A draw — well played." if not cells.has(0) else "Your turn — make a line of three."
	_refresh()
func _refresh() -> void:
	for i in range(9):buttons[i].text="X" if cells[i]==1 else "O" if cells[i]==2 else ""
	status.text=outcome
