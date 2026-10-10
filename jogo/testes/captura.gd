extends Node
## Gera capturas de tela do protótipo em docs/prototipo/.
## Precisa de uma tela (não funciona com --headless). Num servidor sem tela:
##   xvfb-run -a godot --path jogo --rendering-driver opengl3 res://testes/captura.tscn

const ESCALA := 2

var _pasta := ""


func _ready() -> void:
	_pasta = ProjectSettings.globalize_path("res://").path_join("../docs/prototipo").simplify_path()
	DirAccess.make_dir_recursive_absolute(_pasta)

	var principal: Node = load("res://cenas/principal.tscn").instantiate()
	add_child(principal)
	await _esperar(1.0)
	await _capturar("vida_000.png")

	var p: Personagem = principal.personagem
	p.vestir("cabelo", "cabelo_longo")
	p.vestir("cor_cabelo", 3)
	p.vestir("roupa_cima", "casaco")
	p.vestir("cor_roupa_cima", 2)
	p.vestir("chapeu", "chapeu_cogumelo")
	principal.painel.slider.value = 50
	await _esperar(3.5)
	await _capturar("vida_050.png")

	principal.painel.slider.value = 100
	principal.painel.provador.hide()
	await _esperar(3.5)
	await _capturar("vida_100.png")

	principal.queue_free()
	await get_tree().process_frame
	await _vitrine()
	get_tree().quit()


func _vitrine() -> void:
	var fundo := ColorRect.new()
	fundo.color = Color("f4e4c1")
	fundo.size = Vector2(360, 640)
	add_child(fundo)
	var raiz := Node2D.new()
	raiz.scale = Vector2(2, 2)
	add_child(raiz)
	var visuais := [
		{"pele": 1, "cabelo": "cabelo_curto", "cor_cabelo": 2, "roupa_cima": "camiseta", "cor_roupa_cima": 0, "chapeu": ""},
		{"pele": 4, "cabelo": "cabelo_longo", "cor_cabelo": 0, "roupa_cima": "casaco", "cor_roupa_cima": 1, "chapeu": "chapeu_bone"},
		{"pele": 2, "cabelo": "cabelo_longo", "cor_cabelo": 6, "roupa_cima": "camiseta", "cor_roupa_cima": 3, "chapeu": "chapeu_cogumelo"},
		{"pele": 5, "cabelo": "cabelo_curto", "cor_cabelo": 4, "roupa_cima": "casaco", "cor_roupa_cima": 2, "chapeu": "chapeu_gorro"},
	]
	for coluna in visuais.size():
		for linha in 3:
			var p := Personagem.new()
			p.position = Vector2(24 + coluna * 42, 70 + linha * 58)
			raiz.add_child(p)
			for chave in visuais[coluna]:
				p.vestir(chave, visuais[coluna][chave])
			p.direcao = linha
	await _esperar(0.3)
	await _capturar("vitrine.png", Rect2i(0, 30, 360, 360))


func _esperar(segundos: float) -> void:
	await get_tree().create_timer(segundos).timeout


func _capturar(nome: String, recorte := Rect2i()) -> void:
	await RenderingServer.frame_post_draw
	var imagem := get_viewport().get_texture().get_image()
	if recorte.has_area():
		imagem = imagem.get_region(recorte)
	imagem.resize(imagem.get_width() * ESCALA, imagem.get_height() * ESCALA, Image.INTERPOLATE_NEAREST)
	imagem.save_png(_pasta.path_join(nome))
	print("captura: ", _pasta.path_join(nome))
