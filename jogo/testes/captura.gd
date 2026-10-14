extends Node
## Gera capturas de tela do protótipo em docs/prototipo/.
## Precisa de uma tela (não funciona com --headless). Num servidor sem tela:
##   xvfb-run -a godot --path jogo --rendering-driver opengl3 res://testes/captura.tscn

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
	p.vestir("cor_cabelo", 6)
	p.vestir("roupa_cima", "tunica")
	p.vestir("cor_roupa_cima", 1)
	p.vestir("roupa_baixo", "saia")
	p.vestir("cor_roupa_baixo", 6)
	p.vestir("chapeu", "chapeu_cogumelo")
	principal.painel.slider.value = 50
	await _esperar(3.5)
	await _capturar("vida_050.png")

	principal.painel.slider.value = 100
	principal.painel.provador.hide()
	await _esperar(3.5)
	await _capturar("vida_100.png")

	# Mais embaixo na cena, perto do poço.
	principal.vale.ir_para(Vector2(330, 880))
	await _esperar(7.0)
	await _capturar("vida_100_poco.png")

	# Personagem gerado por IA, andando de lado.
	p.vestir("completo", "ia_gemini")
	principal.vale.ir_para(Vector2(150, 880))
	await _esperar(1.2)
	await _capturar("ia_andando.png")

	principal.queue_free()
	await get_tree().process_frame
	await _vitrine()
	get_tree().quit()


func _vitrine() -> void:
	var fundo := ColorRect.new()
	fundo.color = Color("f4e4c1")
	fundo.size = Vector2(540, 960)
	add_child(fundo)
	var raiz := Node2D.new()
	raiz.scale = Vector2(2, 2)
	add_child(raiz)
	var visuais := [
		{"pele": 1, "cabelo": "cabelo_curto", "cor_cabelo": 2, "roupa_cima": "camiseta", "cor_roupa_cima": 0,
			"roupa_baixo": "calca", "cor_roupa_baixo": 1, "chapeu": ""},
		{"pele": 4, "cabelo": "cabelo_longo", "cor_cabelo": 0, "roupa_cima": "moletom", "cor_roupa_cima": 2,
			"roupa_baixo": "calca", "cor_roupa_baixo": 5, "chapeu": "chapeu_broto"},
		{"pele": 0, "cabelo": "cabelo_longo", "cor_cabelo": 6, "roupa_cima": "tunica", "cor_roupa_cima": 1,
			"roupa_baixo": "saia", "cor_roupa_baixo": 6, "chapeu": "chapeu_cogumelo"},
		{"pele": 2, "cabelo": "cabelo_coque", "cor_cabelo": 4, "roupa_cima": "camiseta", "cor_roupa_cima": 4,
			"roupa_baixo": "saia", "cor_roupa_baixo": 3, "chapeu": "chapeu_coroa"},
		{"pele": 5, "cabelo": "cabelo_curto", "cor_cabelo": 3, "roupa_cima": "moletom", "cor_roupa_cima": 3,
			"roupa_baixo": "calca", "cor_roupa_baixo": 7, "chapeu": "chapeu_capuz"},
		{"pele": 3, "cabelo": "cabelo_coque", "cor_cabelo": 7, "roupa_cima": "tunica", "cor_roupa_cima": 6,
			"roupa_baixo": "calca", "cor_roupa_baixo": 1, "chapeu": "chapeu_gorro"},
		{"pele": 1, "cabelo": "cabelo_longo", "cor_cabelo": 9, "roupa_cima": "camiseta", "cor_roupa_cima": 2,
			"roupa_baixo": "saia", "cor_roupa_baixo": 0, "chapeu": "chapeu_nuvem"},
	]
	# Linha de cima: frente; linha do meio: costas; linha de baixo: lado.
	for coluna in 4:
		for linha in 3:
			_vitrine_personagem(raiz, visuais[coluna], Vector2(34 + coluna * 64, 100 + linha * 108), linha)
	for coluna in 3:
		_vitrine_personagem(raiz, visuais[4 + coluna], Vector2(66 + coluna * 64, 100 + 3 * 108 + 40), 0)
	await _esperar(0.3)
	await _capturar("vitrine.png")


func _vitrine_personagem(raiz: Node2D, visual: Dictionary, posicao: Vector2, direcao: int) -> void:
	var p := Personagem.new()
	p.position = posicao
	raiz.add_child(p)
	for chave in visual:
		p.vestir(chave, visual[chave])
	p.direcao = direcao


func _esperar(segundos: float) -> void:
	await get_tree().create_timer(segundos).timeout


func _capturar(nome: String) -> void:
	await RenderingServer.frame_post_draw
	var imagem := get_viewport().get_texture().get_image()
	imagem.save_png(_pasta.path_join(nome))
	print("captura: ", _pasta.path_join(nome))
