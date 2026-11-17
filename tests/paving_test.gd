extends SceneTree
const P=preload("res://scripts/lunar_paving.gd")
func _initialize() -> void:
	var rows: Array=preload("res://scripts/map_data.gd").AREAS.main.floor
	var before:=Time.get_ticks_msec()
	var map:=P.bake(rows)
	assert(map.get_size()==Vector2i(3696,3056))
	assert(map.get_pixel(115*16,95*16).a==1)
	assert(map.get_pixel(0,0).a==0)
	map.save_png("res://review/floor_map_native.png")
	for k in range(6):
		var img:=Image.create(192,128,false,Image.FORMAT_RGBA8)
		for y in range(128):
			for x in range(192):img.set_pixel(x,y,P.swatch(k,x,y))
		img.save_png("res://review/floor_variant_%d.png"%k)
		var samples: Array[PackedByteArray]=[]
		for v in range(3):
			var sample:=Image.create(192,128,false,Image.FORMAT_RGBA8)
			for y in range(128):
				for x in range(192):sample.set_pixel(x,y,P.swatch(k,x,y,v))
			assert(sample.get_data()!=img.get_data())
			for prior in samples:assert(sample.get_data()!=prior)
			samples.append(sample.get_data())
			sample.save_png("res://review/floor_%d_subvariant_%d.png"%[k,v])
	print("PASS: 18 distinct subvariants, six mixed surfaces and floor map exported in ",Time.get_ticks_msec()-before," ms; walls remain transparent.")
	quit()
