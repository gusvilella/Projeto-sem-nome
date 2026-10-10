extends Node
## Testes automáticos do protótipo da Fase 0.
## Rodar: godot --headless --path jogo res://testes/teste_prototipo.tscn

var _falhas := 0
var _total := 0


func _ready() -> void:
	_testar_dados()
	_testar_arte()
	_testar_mapa()
	var principal: Node = load("res://cenas/principal.tscn").instantiate()
	add_child(principal)
	await get_tree().process_frame
	_testar_personagem(principal.personagem)
	_testar_marcos(principal.vale)
	_testar_caminho(principal.vale)
	_testar_provador(principal.painel)
	print("\n%d verificações, %d falha(s)" % [_total, _falhas])
	get_tree().quit(1 if _falhas > 0 else 0)


func verificar(condicao: bool, descricao: String) -> void:
	_total += 1
	if not condicao:
		_falhas += 1
		printerr("FALHOU: " + descricao)


func _testar_dados() -> void:
	verificar(Dados.lista_paletas("pele").size() == 6, "6 tons de pele")
	verificar(Dados.lista_paletas("cabelo").size() == 10, "10 cores de cabelo")
	verificar(Dados.lista_paletas("roupa").size() >= 6, "cores de roupa")
	for grupo in ["pele", "cabelo", "roupa"]:
		for i in Dados.lista_paletas(grupo).size():
			verificar(Dados.cores_da_paleta(grupo, i).size() == 4, "paleta %s/%d tem 4 cores" % [grupo, i])
	verificar(Dados.ancoras["parado"].size() == 2, "2 quadros parado")
	verificar(Dados.ancoras["andar"].size() == 4, "4 quadros andando")
	verificar(Dados.regioes.has("casa"), "região casa carregada")
	var ids := {}
	for item in Dados.itens:
		verificar(not ids.has(item["id"]), "id único: " + item["id"])
		ids[item["id"]] = true
		verificar(item.get("gratis", false) or item.has("preco_faiscas"), "item %s é grátis ou tem preço" % item["id"])


func _testar_arte() -> void:
	var texturas := []
	for chave in Dados.base_personagem:
		texturas.append([chave, Dados.base_personagem[chave]])
	for item in Dados.itens:
		texturas.append([item["tipo"], item["textura"]])
		if item.has("textura_tras"):
			texturas.append(["cabelo_tras", item["textura_tras"]])
	for par in texturas:
		var caminho: String = par[1]
		verificar(ResourceLoader.exists(caminho), "textura existe: " + caminho)
		var tex: Texture2D = load(caminho)
		if tex == null:
			continue
		match par[0]:
			"sombra":
				verificar(tex.get_size() == Vector2(32, 48), "sombra 32x48")
			"cabelo", "cabelo_tras", "chapeu", "rosto":
				verificar(tex.get_width() == 96 and tex.get_height() in [48, 96], "camada de cabeça 3 x 1 ou 3 x 2: " + caminho)
			_:
				verificar(tex.get_size() == Vector2(192, 144), "camada de corpo 6 x 3: " + caminho)


func _testar_mapa() -> void:
	var mapa := Dados.ler_json(Dados.regioes["casa"]["mapa"])
	var linhas: Array = mapa["linhas"]
	for i in linhas.size():
		verificar(linhas[i].length() == linhas[0].length(), "linha %d do mapa com largura certa" % i)
	verificar(linhas.size() * 16 >= 640, "mapa cobre a altura da tela")
	verificar(linhas[0].length() * 16 >= 360, "mapa cobre a largura da tela")


func _testar_personagem(p: Personagem) -> void:
	verificar(p.sprite("corpo").material is ShaderMaterial, "corpo usa troca de paleta")
	verificar(p.sprite("rosto").material == null, "rosto não usa paleta")
	verificar(p.sprite("cabelo_tras").texture == null, "cabelo curto não tem camada de trás")

	p.vestir("cabelo", "cabelo_longo")
	verificar(p.sprite("cabelo_tras").texture != null, "cabelo longo tem camada de trás")

	p.vestir("chapeu", "chapeu_bone")
	verificar(p.sprite("cabelo_frente").frame >= 3, "boné usa o cabelo recortado")
	p.vestir("chapeu", "chapeu_gorro")
	verificar(p.sprite("cabelo_frente").texture == null, "gorro esconde todo o cabelo")
	verificar(p.sprite("cabelo_tras").texture == null, "gorro esconde o cabelo de trás")
	p.vestir("chapeu", "")
	verificar(p.sprite("cabelo_frente").frame < 3, "sem chapéu usa o cabelo inteiro")

	p.vestir("cor_cabelo", 3)
	var cor: Color = p.sprite("cabelo_frente").material.get_shader_parameter("cor_base")
	verificar(cor.is_equal_approx(Color.html(Dados.lista_paletas("cabelo")[3]["cores"][2])), "cor do cabelo aplicada")
	p.vestir("cabelo", "cabelo_curto")
	p.vestir("cor_cabelo", 2)


func _testar_marcos(v: Vale) -> void:
	verificar(not v.marco_ativo("flores"), "flores escondidas com vida 0")
	var alcancados := []
	var ao_alcancar := func(m): alcancados.append(m["elemento"])
	v.marco_alcancado.connect(ao_alcancar)
	v.definir_vida(60)
	verificar(v.marco_ativo("flores") and v.marco_ativo("fumaca"), "flores e fumaça com vida 60")
	verificar(not v.marco_ativo("luz"), "luz ainda apagada com vida 60")
	verificar(alcancados == ["flores", "fumaca"], "sinal de marco emitido em ordem")
	verificar(v.proximo_marco().get("elemento") == "luz", "próximo marco é a luz")
	v.definir_vida(100)
	verificar(v.proximo_marco().is_empty(), "todos os marcos com vida 100")
	v.marco_alcancado.disconnect(ao_alcancar)
	v.definir_vida(0, true)


func _testar_caminho(v: Vale) -> void:
	verificar(not v.astar.is_point_solid(v.inicio), "início do personagem é livre")
	verificar(not v.ir_para(Vector2(-50, -50)), "não anda para fora do mapa")
	var lago := Vector2(6, 30) * 16 + Vector2(8, 8)
	verificar(not v.ir_para(lago), "não anda para dentro do lago")

	# Andar até o piso de pedra em frente à porta, logo acima do início.
	var porta := Vector2i(v.inicio.x, 13)
	verificar(v.ir_para(v.centro_da_celula(porta)), "encontra caminho até a porta")
	var p := v.personagem
	var celulas_pisadas := {}
	for i in 600:
		if not p.esta_andando():
			break
		p._process(1.0 / 30.0)
		celulas_pisadas[Vector2i((p.position / 16).floor())] = true
	verificar(p.position.distance_to(v.centro_da_celula(porta)) < 0.5, "chegou à porta")
	var pisou_em_solido := false
	for c in celulas_pisadas:
		if v.astar.is_point_solid(c):
			pisou_em_solido = true
	verificar(not pisou_em_solido, "nunca pisou em tile sólido")
	verificar(p.direcao == Personagem.Direcao.CIMA, "terminou olhando para a porta (cima)")


func _testar_provador(painel: PainelPrototipo) -> void:
	var antes = painel.personagem.aparencia["chapeu"]
	painel.trocar("chapeu", 1)
	verificar(painel.personagem.aparencia["chapeu"] != antes, "provador troca o chapéu")
	painel.trocar("chapeu", -1)
	verificar(painel.personagem.aparencia["chapeu"] == antes, "provador volta o chapéu")
	verificar(painel.valores_da_opcao("cabelo").size() == Dados.itens_do_tipo("cabelo").size(), "provador lista os cabelos")
	painel.slider.value = 30
	verificar(painel.vale.vida == 30, "slider muda a vida da região")
