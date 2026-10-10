class_name Vale
extends Node2D
## Uma região do Vale: chão em tiles, objetos com ordenação por Y, caminhos por
## toque e o efeito de mundo desbotado que ganha cor conforme a vida sobe.
## Ver docs/gdd/01-loop-principal.md#o-mundo-que-ganha-cor.

signal marco_alcancado(marco: Dictionary)

const TILE := 16
## Caractere do mapa -> coluna no atlas arte/cenario/tiles.png.
const CHAO := {".": 0, ",": 1, "*": 2, "=": 3, "~": 4, "#": 5, "o": 6, "|": 7}
const CHAO_SOLIDO := ["~", "#", "|"]
const BASE_CASA := Vector2i(5, 2)
const CHAMINE := Vector2(20, -72)  # topo da chaminé, relativo à base da casa
const DURACAO_TRANSICAO := 0.8

var regiao: Dictionary
var tamanho := Vector2i.ZERO
var inicio := Vector2i.ZERO
var vida := 0.0
var astar := AStarGrid2D.new()
var personagem: Personagem

var _material := ShaderMaterial.new()
var _chao := TileMapLayer.new()
## elemento do marco -> nós que aparecem quando ele é alcançado
var _elementos := {"flores": [], "fumaca": [], "luz": [], "borboletas": []}
var _marcos_ativos := {}
var _casa: Sprite2D
var _tempo_fumaca := 0.0
var _tempo := 0.0


func _init(id_regiao := "casa") -> void:
	regiao = Dados.regioes[id_regiao]


func _ready() -> void:
	y_sort_enabled = true
	_material.shader = preload("res://shaders/dessaturacao.gdshader")
	material = _material
	_construir(Dados.ler_json(regiao["mapa"]))
	definir_vida(0.0, true)


func _construir(mapa: Dictionary) -> void:
	var linhas: Array = mapa["linhas"]
	tamanho = Vector2i(linhas[0].length(), linhas.size())
	inicio = Vector2i(mapa["inicio"][0], mapa["inicio"][1])

	_chao.name = "Chao"
	_chao.tile_set = _criar_tileset()
	_chao.use_parent_material = true
	_chao.z_index = -1
	add_child(_chao)

	astar.region = Rect2i(Vector2i.ZERO, tamanho)
	astar.cell_size = Vector2(TILE, TILE)
	astar.offset = Vector2(TILE, TILE) / 2.0
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	astar.update()

	for y in tamanho.y:
		for x in tamanho.x:
			var c: String = linhas[y][x]
			var celula := Vector2i(x, y)
			_chao.set_cell(celula, 0, Vector2i(CHAO.get(c, 0), 0))
			if c in CHAO_SOLIDO:
				astar.set_point_solid(celula)
			var pe := Vector2(x * TILE + TILE / 2.0, (y + 1) * TILE)
			match c:
				"T":
					_criar_objeto("res://arte/cenario/arvore.png", pe, Vector2(-16, -46))
					astar.set_point_solid(celula)
				"C":
					_criar_casa(celula)
				"f":
					_elementos["flores"].append(
						_criar_objeto("res://arte/cenario/flores_altas.png", pe, Vector2(-8, -16)))
				"b":
					_elementos["borboletas"].append(_criar_borboleta(pe + Vector2(0, -TILE)))


func _criar_tileset() -> TileSet:
	var tileset := TileSet.new()
	tileset.tile_size = Vector2i(TILE, TILE)
	var atlas := TileSetAtlasSource.new()
	atlas.texture = preload("res://arte/cenario/tiles.png")
	atlas.texture_region_size = Vector2i(TILE, TILE)
	for i in int(atlas.texture.get_width() / float(TILE)):
		atlas.create_tile(Vector2i(i, 0))
	tileset.add_source(atlas, 0)
	return tileset


func _criar_objeto(caminho: String, pe: Vector2, deslocamento: Vector2) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load(caminho)
	s.centered = false
	s.offset = deslocamento
	s.position = pe
	s.use_parent_material = true
	add_child(s)
	return s


## A casa ocupa uma base sólida de 5 x 2 tiles; "C" marca o canto inferior esquerdo.
func _criar_casa(canto: Vector2i) -> void:
	var pe := Vector2((canto.x * TILE) + BASE_CASA.x * TILE / 2.0, (canto.y + 1) * TILE)
	_casa = _criar_objeto("res://arte/cenario/casa.png", pe, Vector2(-40, -72))
	var luz := _criar_objeto("res://arte/cenario/casa_luz.png", pe, Vector2(-40, -72))
	_elementos["luz"].append(luz)
	for dy in BASE_CASA.y:
		for dx in BASE_CASA.x:
			astar.set_point_solid(canto + Vector2i(dx, -dy))


func _criar_borboleta(origem: Vector2) -> Sprite2D:
	var s := _criar_objeto("res://arte/cenario/borboleta.png", origem, Vector2(-4, -4))
	s.hframes = 2
	s.z_index = 1
	s.set_meta("origem", origem)
	s.set_meta("fase", randf() * TAU)
	return s


func adicionar_personagem(p: Personagem) -> void:
	personagem = p
	personagem.position = centro_da_celula(inicio)
	add_child(personagem)


func centro_da_celula(celula: Vector2i) -> Vector2:
	return Vector2(celula) * TILE + Vector2(TILE, TILE) / 2.0


func tamanho_em_pixels() -> Vector2i:
	return tamanho * TILE


# --- Toque para andar -----------------------------------------------------

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if ir_para(get_global_mouse_position()):
			get_viewport().set_input_as_handled()


## Calcula o caminho até o ponto tocado e manda o personagem andar.
func ir_para(ponto: Vector2) -> bool:
	if personagem == null:
		return false
	var destino := Vector2i((ponto / TILE).floor())
	if not astar.is_in_boundsv(destino) or astar.is_point_solid(destino):
		return false
	var origem := Vector2i((personagem.position / TILE).floor())
	var caminho := astar.get_point_path(origem, destino)
	if caminho.is_empty():
		return false
	# Se já está a caminho do segundo ponto, não volta para o centro do tile atual.
	if caminho.size() > 1 and personagem.position.distance_to(caminho[1]) < TILE:
		caminho.remove_at(0)
	personagem.andar_por(caminho)
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
		for no in _elementos[elemento]:
			_mostrar(no, ativo, instantaneo)
		if ativo and not era_ativo:
			marco_alcancado.emit(marco)


func marco_ativo(elemento: String) -> bool:
	return _marcos_ativos.get(elemento, false)


## Próximo marco ainda não alcançado, ou {} se todos foram.
func proximo_marco() -> Dictionary:
	for marco in regiao["marcos"]:
		if vida < marco["vida"]:
			return marco
	return {}


func _mostrar(no: CanvasItem, ativo: bool, instantaneo: bool) -> void:
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
	for b in _elementos["borboletas"]:
		var fase: float = b.get_meta("fase")
		var origem: Vector2 = b.get_meta("origem")
		b.position = origem + Vector2(sin(_tempo * 0.7 + fase) * 20.0, cos(_tempo * 1.3 + fase) * 8.0)
		b.frame = int(_tempo * 8.0 + fase) % 2
	if marco_ativo("fumaca") and _casa != null:
		_tempo_fumaca -= delta
		if _tempo_fumaca <= 0.0:
			_tempo_fumaca = 0.9
			_soltar_fumaca()


func _soltar_fumaca() -> void:
	var s := _criar_objeto("res://arte/cenario/fumaca.png", _casa.position + CHAMINE, Vector2(-8, -8))
	s.z_index = 1
	s.scale = Vector2.ONE * 0.5
	var tween := create_tween().set_parallel()
	tween.tween_property(s, "position", s.position + Vector2(randf_range(4, 12), -28), 2.4)
	tween.tween_property(s, "scale", Vector2.ONE, 2.4)
	tween.tween_property(s, "modulate:a", 0.0, 2.4).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(s.queue_free)
