extends Node
## Testes automáticos do protótipo da Fase 0.
## Rodar: godot --headless --path jogo res://testes/teste_prototipo.tscn

var _falhas := 0
var _total := 0


func _ready() -> void:
	_testar_dados()
	_testar_arte()
	_testar_cena()
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
			verificar(Dados.cores_da_paleta(grupo, i).size() == 8, "paleta %s/%d tem 8 tons" % [grupo, i])
	var colunas: Dictionary = Dados.ancoras["colunas"]
	verificar(colunas["parado"].size() == 2, "2 quadros parado")
	verificar(colunas["andar"].size() == 4, "4 quadros andando")
	for direcao in ["baixo", "cima", "lado"]:
		verificar(Dados.ancoras["cabeca"][direcao].size() == 6, "âncora de cabeça para os 6 quadros (%s)" % direcao)
	verificar(Dados.regioes.has("casa"), "região casa carregada")
	var ids := {}
	for item in Dados.itens:
		verificar(not ids.has(item["id"]), "id único: " + item["id"])
		ids[item["id"]] = true
		verificar(item.get("gratis", false) or item.has("preco_faiscas"), "item %s é grátis ou tem preço" % item["id"])


func _testar_arte() -> void:
	var corpo := Dados.vetor(Dados.ancoras["quadro_corpo"])
	var cabeca := Dados.vetor(Dados.ancoras["quadro_cabeca"])
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
				verificar(tex.get_size() == corpo, "sombra do tamanho do quadro do corpo")
			"cabelo", "cabelo_tras", "chapeu", "rosto":
				verificar(tex.get_width() == cabeca.x * 3 and float(tex.get_height()) in [cabeca.y, cabeca.y * 2],
						"camada de cabeça 3 x 1 ou 3 x 2: " + caminho)
			_:
				verificar(tex.get_size() == corpo * Vector2(6, 3), "camada de corpo 6 x 3: " + caminho)


func _testar_cena() -> void:
	var regiao: Dictionary = Dados.regioes["casa"]
	var cena: Dictionary = regiao["cena"]
	var tamanho := Dados.vetor(cena["tamanho"])
	for chave in ["fundo", "caminhavel"]:
		var tex: Texture2D = load(cena[chave])
		verificar(tex != null and tex.get_size() == tamanho, "%s do tamanho da cena" % chave)
	verificar(tamanho.x >= 540 and tamanho.y >= 960, "cena cobre a tela")
	for o in cena["objetos"]:
		verificar(ResourceLoader.exists(o["textura"]), "objeto existe: " + o["textura"])
	for marco in regiao["marcos"]:
		for camada in marco.get("camadas", []):
			verificar(ResourceLoader.exists(camada["textura"]), "camada de marco existe: " + camada["textura"])
			if camada.has("acima_de"):
				verificar(int(camada["acima_de"]) < cena["objetos"].size(), "camada acima de um objeto válido")


func _testar_personagem(p: Personagem) -> void:
	verificar(p.sprite("corpo").material is ShaderMaterial, "corpo usa troca de paleta")
	verificar(p.sprite("rosto").material == null, "rosto não usa paleta")
	verificar(p.sprite("cabelo_tras").texture == null, "cabelo curto não tem camada de trás")

	p.vestir("cabelo", "cabelo_longo")
	verificar(p.sprite("cabelo_tras").texture != null, "cabelo longo tem camada de trás")

	p.vestir("chapeu", "chapeu_gorro")
	verificar(p.sprite("cabelo_frente").frame >= 3, "gorro usa o cabelo recortado")
	p.vestir("chapeu", "chapeu_capuz")
	verificar(p.sprite("cabelo_frente").texture == null, "capuz esconde todo o cabelo")
	verificar(p.sprite("cabelo_tras").texture == null, "capuz esconde o cabelo de trás")
	p.vestir("chapeu", "chapeu_broto")
	verificar(p.sprite("cabelo_frente").frame < 3, "broto não recorta o cabelo")
	p.vestir("chapeu", "")

	p.vestir("cor_cabelo", 3)
	var cores: PackedColorArray = p.sprite("cabelo_frente").material.get_shader_parameter("cores")
	verificar(cores.size() == 8 and cores[5].is_equal_approx(Color.html(Dados.lista_paletas("cabelo")[3]["cores"][5])),
			"cor do cabelo aplicada")
	p.vestir("cabelo", "cabelo_curto")
	p.vestir("cor_cabelo", 2)

	p.vestir("completo", "ia_gemini")
	verificar(p.sprite("corpo").texture != null and p.sprite("corpo").material == null, "personagem completo no corpo, sem paleta")
	verificar(p.sprite("cabelo_frente").texture == null and p.sprite("roupa_cima").texture == null, "personagem completo esconde as camadas")
	p.vestir("chapeu", "ia_chapeu_cogumelo")
	verificar(p.sprite("chapeu").texture != null, "chapéu de IA aparece no personagem de IA")
	p.vestir("completo", "")
	verificar(p.sprite("roupa_cima").texture != null, "volta para as camadas")
	verificar(p.sprite("chapeu").texture == null, "chapéu de IA não aparece no personagem em camadas")
	p.vestir("chapeu", "")

	# A cabeça acompanha o corpo, inclusive espelhada.
	var ancora := Dados.vetor(Dados.ancoras["cabeca"]["lado"][0]) - Dados.vetor(Dados.ancoras["pes"])
	p.direcao = Personagem.Direcao.LADO
	p.virado_para_esquerda = false
	p._atualizar_quadro()
	verificar(p.sprite("rosto").position == ancora, "rosto na âncora (virado para a direita)")
	p.virado_para_esquerda = true
	p._atualizar_quadro()
	verificar(p.sprite("rosto").position == Vector2(-ancora.x, ancora.y), "rosto espelhado (virado para a esquerda)")
	p.direcao = Personagem.Direcao.BAIXO
	p.virado_para_esquerda = false


func _testar_marcos(v: Vale) -> void:
	verificar(not v.marco_ativo("flores"), "flores escondidas com vida 0")
	for no in v.elementos_do_marco("luz"):
		verificar(not no.visible, "luzes apagadas com vida 0")
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
	var tem_folhas := false
	for no in v.elementos_do_marco("borboletas"):
		if no is CPUParticles2D:
			tem_folhas = no.emitting
	verificar(tem_folhas, "folhas caindo com vida 100")
	v.marco_alcancado.disconnect(ao_alcancar)
	v.definir_vida(0, true)


func _andar_ate_parar(v: Vale) -> Array:
	var p := v.personagem
	var pisou_em_solido := false
	for i in 2000:
		if not p.esta_andando():
			break
		p._process(1.0 / 30.0)
		if not v.livre(p.position):
			pisou_em_solido = true
	return [pisou_em_solido]


func _testar_caminho(v: Vale) -> void:
	var p := v.personagem
	verificar(v.livre(v.inicio), "início do personagem é livre")
	verificar(not v.ir_para(Vector2(-50, -50)), "não anda para fora da cena")

	# Até a porta, logo acima do início.
	var porta := Vector2(v.inicio.x, 450)
	verificar(v.ir_para(porta), "encontra caminho até a porta")
	var r := _andar_ate_parar(v)
	verificar(p.position.distance_to(porta) < 0.5, "chegou à porta")
	verificar(not r[0], "não atravessou obstáculos até a porta")
	verificar(p.direcao == Personagem.Direcao.CIMA, "terminou olhando para a porta (cima)")

	# Para baixo do poço: precisa contornar o poço.
	var depois_do_poco := Vector2(270, 880)
	verificar(not v.livre(Vector2(270, 800)), "o poço é obstáculo")
	verificar(v.ir_para(depois_do_poco), "encontra caminho contornando o poço")
	r = _andar_ate_parar(v)
	verificar(p.position.distance_to(depois_do_poco) < 0.5, "chegou depois do poço")
	verificar(not r[0], "não atravessou o poço")

	# Tocar em cima de um obstáculo leva ao ponto livre mais próximo.
	verificar(v.ir_para(Vector2(270, 800)), "tocar no poço anda até perto dele")
	_andar_ate_parar(v)
	verificar(v.livre(p.position) and p.position.distance_to(Vector2(270, 800)) < 80, "parou perto do poço")


func _testar_provador(painel: PainelPrototipo) -> void:
	var antes = painel.personagem.aparencia["chapeu"]
	painel.trocar("chapeu", 1)
	verificar(painel.personagem.aparencia["chapeu"] != antes, "provador troca o chapéu")
	painel.trocar("chapeu", -1)
	verificar(painel.personagem.aparencia["chapeu"] == antes, "provador volta o chapéu")
	verificar(painel.valores_da_opcao("cabelo").size() == Dados.itens_do_tipo("cabelo").size(), "provador lista os cabelos")
	var chapeus_camadas := painel.valores_da_opcao("chapeu").size()
	painel.trocar("completo", 1)
	verificar(painel.personagem.aparencia["completo"] == "ia_gemini", "provador troca para o personagem de IA")
	verificar(painel.valores_da_opcao("chapeu").size() == 11 and chapeus_camadas == 7, "provador lista só os chapéus de cada visual")
	painel.trocar("completo", -1)
	painel.slider.value = 30
	verificar(painel.vale.vida == 30, "slider muda a vida da região")
