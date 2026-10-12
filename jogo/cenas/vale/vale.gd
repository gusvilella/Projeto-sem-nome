class_name Vale
extends Node2D
## Uma região do Vale como cena ilustrada: fundo pintado, objetos com ordenação
## por profundidade, área caminhável vinda de uma máscara, toque para andar e o
## mundo desbotado que ganha cor (e luz quente) conforme a vida sobe.
## Ver docs/gdd/05-direcao-de-arte.md#regiões-como-cenas-ilustradas.

signal marco_alcancado(marco: Dictionary)

## Tamanho da célula da grade de caminhos, em pixels.
const CELULA := 8
const DURACAO_TRANSICAO := 0.8
## Até quantas células de distância procurar um ponto livre quando o toque cai num obstáculo.
const BUSCA_PONTO_LIVRE := 8

var regiao: Dictionary
var cena: Dictionary
var tamanho := Vector2i.ZERO
var inicio := Vector2.ZERO
var vida := 0.0
var astar := AStarGrid2D.new()
var personagem: Personagem
var objetos: Array[Sprite2D] = []

var _material := ShaderMaterial.new()
## elemento do marco -> nós que aparecem quando ele é alcançado
var _elementos := {}
var _marcos_ativos := {}
var _chamine := Vector2.ZERO
var _folhas: CPUParticles2D
var _tempo_fumaca := 0.0
var _tempo := 0.0


func _init(id_regiao := "casa") -> void:
	regiao = Dados.regioes[id_regiao]
	cena = regiao["cena"]


func _ready() -> void:
	y_sort_enabled = true
	_material.shader = preload("res://shaders/dessaturacao.gdshader")
	material = _material
	_construir()
	definir_vida(0.0, true)


func _construir() -> void:
	tamanho = Vector2i(cena["tamanho"][0], cena["tamanho"][1])
	inicio = Dados.vetor(cena["inicio"])
	_chamine = Dados.vetor(cena["chamine"])

	var fundo := Sprite2D.new()
	fundo.name = "Fundo"
	fundo.texture = load(cena["fundo"])
	fundo.centered = false
	fundo.use_parent_material = true
	fundo.z_index = -2
	add_child(fundo)

	for o in cena["objetos"]:
		objetos.append(_criar_objeto(o))

	for marco in regiao["marcos"]:
		var nos: Array = []
		for camada in marco.get("camadas", []):
			nos.append(_criar_camada(camada))
		for b in marco.get("borboletas", []):
			nos.append(_criar_borboleta(Dados.vetor(b)))
		if marco["elemento"] == "borboletas":
			_folhas = _criar_folhas()
			nos.append(_folhas)
		_elementos[marco["elemento"]] = nos

	_construir_caminhos(load(cena["caminhavel"]).get_image())


func _criar_objeto(dados: Dictionary) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(dados["textura"])
	s.centered = false
	var ancora := Dados.vetor(dados["ancora"])
	if dados.get("espelhar", false):
		s.flip_h = true
		ancora.x = s.texture.get_width() - ancora.x
	s.offset = -ancora
	s.position = Dados.vetor(dados["pe"])
	s.use_parent_material = true
	add_child(s)
	return s


## Camada de um marco: no chão, por cima de um objeto, ou solta na cena.
func _criar_camada(dados: Dictionary) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(dados["textura"])
	s.centered = false
	s.offset = -Dados.vetor(dados["ancora"])
	s.use_parent_material = true
	var pe := Dados.vetor(dados["pe"])
	if dados.get("chao", false):
		s.position = pe
		s.z_index = -1
		add_child(s)
	elif dados.has("acima_de"):
		var dono := objetos[int(dados["acima_de"])]
		s.position = pe - dono.position
		dono.add_child(s)
	else:
		s.position = pe
		add_child(s)
	return s


func _criar_borboleta(origem: Vector2) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = preload("res://arte/cenario/comum/borboleta.png")
	s.hframes = 2
	s.position = origem
	s.z_index = 1
	s.set_meta("origem", origem)
	s.set_meta("fase", randf() * TAU)
	add_child(s)
	return s


func _criar_folhas() -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.texture = preload("res://arte/cenario/comum/folha.png")
	p.amount = 28
	p.lifetime = 9.0
	p.preprocess = 9.0
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = Vector2(tamanho) / 2.0
	p.position = Vector2(tamanho) / 2.0
	p.direction = Vector2(0.4, 1)
	p.spread = 25.0
	p.gravity = Vector2(6, 10)
	p.initial_velocity_min = 8.0
	p.initial_velocity_max = 18.0
	p.angular_velocity_min = -60.0
	p.angular_velocity_max = 60.0
	p.z_index = 2
	add_child(p)
	return p


func _construir_caminhos(mascara: Image) -> void:
	var celulas := Vector2i(ceili(tamanho.x / float(CELULA)), ceili(tamanho.y / float(CELULA)))
	astar.region = Rect2i(Vector2i.ZERO, celulas)
	astar.cell_size = Vector2(CELULA, CELULA)
	astar.offset = Vector2(CELULA, CELULA) / 2.0
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	astar.update()
	for y in celulas.y:
		for x in celulas.x:
			var px := mini(x * CELULA + (CELULA >> 1), mascara.get_width() - 1)
			var py := mini(y * CELULA + (CELULA >> 1), mascara.get_height() - 1)
			if mascara.get_pixel(px, py).r < 0.5:
				astar.set_point_solid(Vector2i(x, y))


func adicionar_personagem(p: Personagem) -> void:
	personagem = p
	personagem.position = inicio
	add_child(personagem)


func celula_de(ponto: Vector2) -> Vector2i:
	return Vector2i((ponto / CELULA).floor())


func livre(ponto: Vector2) -> bool:
	var c := celula_de(ponto)
	return astar.is_in_boundsv(c) and not astar.is_point_solid(c)


# --- Toque para andar -----------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if ir_para(get_global_mouse_position()):
			get_viewport().set_input_as_handled()


## Calcula o caminho até o ponto tocado e manda o personagem andar.
## Se o toque cair num obstáculo, anda até o ponto livre mais próximo.
func ir_para(ponto: Vector2) -> bool:
	if personagem == null:
		return false
	var destino := celula_de(ponto)
	if not astar.is_in_boundsv(destino):
		return false
	if astar.is_point_solid(destino):
		destino = _celula_livre_perto(destino)
		if destino.x < 0:
			return false
		ponto = astar.get_point_position(destino)
	var caminho := astar.get_point_path(celula_de(personagem.position), destino)
	if caminho.is_empty():
		return false
	caminho[caminho.size() - 1] = ponto
	personagem.andar_por(_suavizar(personagem.position, caminho))
	return true


func _celula_livre_perto(celula: Vector2i) -> Vector2i:
	for raio in range(1, BUSCA_PONTO_LIVRE + 1):
		var melhor := Vector2i(-1, -1)
		var melhor_dist := INF
		for dy in range(-raio, raio + 1):
			for dx in range(-raio, raio + 1):
				var c := celula + Vector2i(dx, dy)
				if astar.is_in_boundsv(c) and not astar.is_point_solid(c) and Vector2(dx, dy).length() < melhor_dist:
					melhor = c
					melhor_dist = Vector2(dx, dy).length()
		if melhor.x >= 0:
			return melhor
	return Vector2i(-1, -1)


## Corta os degraus da grade: pula direto para o ponto mais distante visível.
func _suavizar(de: Vector2, pontos: PackedVector2Array) -> PackedVector2Array:
	var resultado := PackedVector2Array()
	var atual := de
	var i := 0
	while i < pontos.size():
		var j := pontos.size() - 1
		while j > i and not _linha_livre(atual, pontos[j]):
			j -= 1
		resultado.append(pontos[j])
		atual = pontos[j]
		i = j + 1
	return resultado


func _linha_livre(a: Vector2, b: Vector2) -> bool:
	var passos := maxi(1, ceili(a.distance_to(b) / 3.0))
	for k in passos + 1:
		if not livre(a.lerp(b, k / float(passos))):
			return false
	return true


# --- Vida e marcos --------------------------------------------------------

## Vida da região de 0 a 100. No jogo ela só sobe; o protótipo permite descer para testes.
func definir_vida(valor: float, instantaneo := false) -> void:
	vida = clampf(valor, 0.0, 100.0)
	_material.set_shader_parameter("vida", vida / 100.0)
	for marco in regiao["marcos"]:
		var ativo: bool = vida >= marco["vida"]
		var elemento: String = marco["elemento"]
		if _marcos_ativos.has(elemento) and _marcos_ativos[elemento] == ativo:
			continue
		var era_ativo: bool = _marcos_ativos.get(elemento, false)
		_marcos_ativos[elemento] = ativo
		for no in _elementos.get(elemento, []):
			_mostrar(no, ativo, instantaneo)
		if ativo and not era_ativo:
			marco_alcancado.emit(marco)


func marco_ativo(elemento: String) -> bool:
	return _marcos_ativos.get(elemento, false)


func elementos_do_marco(elemento: String) -> Array:
	return _elementos.get(elemento, [])


## Próximo marco ainda não alcançado, ou {} se todos foram.
func proximo_marco() -> Dictionary:
	for marco in regiao["marcos"]:
		if vida < marco["vida"]:
			return marco
	return {}


func _mostrar(no: CanvasItem, ativo: bool, instantaneo: bool) -> void:
	if no is CPUParticles2D:
		no.emitting = ativo
		no.visible = ativo
		return
	var alvo := 1.0 if ativo else 0.0
	if instantaneo:
		no.modulate.a = alvo
		no.visible = ativo
		return
	no.visible = true
	var tween := create_tween()
	tween.tween_property(no, "modulate:a", alvo, DURACAO_TRANSICAO)
	if not ativo:
		tween.tween_callback(no.hide)


func _process(delta: float) -> void:
	_tempo += delta
	for b in _elementos.get("borboletas", []):
		if b is Sprite2D:
			var fase: float = b.get_meta("fase")
			var origem: Vector2 = b.get_meta("origem")
			b.position = origem + Vector2(sin(_tempo * 0.7 + fase) * 26.0, cos(_tempo * 1.3 + fase) * 10.0)
			b.frame = int(_tempo * 8.0 + fase) % 2
	if marco_ativo("fumaca"):
		_tempo_fumaca -= delta
		if _tempo_fumaca <= 0.0:
			_tempo_fumaca = 0.8
			_soltar_fumaca()


func _soltar_fumaca() -> void:
	var s := Sprite2D.new()
	s.texture = preload("res://arte/cenario/comum/fumaca.png")
	s.position = _chamine
	s.z_index = 1
	s.scale = Vector2.ONE * 0.6
	s.use_parent_material = true
	add_child(s)
	var tween := create_tween().set_parallel()
	tween.tween_property(s, "position", s.position + Vector2(randf_range(6, 16), -40), 2.8)
	tween.tween_property(s, "scale", Vector2.ONE * 1.4, 2.8)
	tween.tween_property(s, "modulate:a", 0.0, 2.8).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(s.queue_free)
