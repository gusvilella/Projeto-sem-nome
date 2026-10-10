class_name Personagem
extends Node2D
## Personagem montado em camadas (paper doll).
## Ver docs/gdd/05-direcao-de-arte.md#personagem-em-camadas-paper-doll.

signal chegou

enum Direcao { BAIXO, CIMA, LADO }

const VELOCIDADE := 64.0
const QUADROS_POR_SEGUNDO := {"parado": 2.0, "andar": 8.0}
const PRIMEIRA_COLUNA := {"parado": 0, "andar": 2}
const COLUNAS_CORPO := 6
## Põe os pés do quadro 32 x 48 na origem do nó.
const DESLOCAMENTO_QUADRO := Vector2(-16, -46)

## Ordem de desenho, de baixo para cima.
const CAMADAS := [
	"sombra", "cabelo_tras", "corpo", "rosto", "roupa_baixo",
	"calcado", "roupa_cima", "cabelo_frente", "chapeu",
]
## Camadas desenhadas uma vez por direção, que seguem a âncora de cabeça.
const CAMADAS_DE_CABECA := ["cabelo_tras", "rosto", "cabelo_frente", "chapeu"]

var direcao: Direcao = Direcao.BAIXO
var virado_para_esquerda := false
var animacao := "parado"

## Aparência atual. Índices de cor apontam para data/personagem/paletas.json.
var aparencia := {
	"pele": 1,
	"cabelo": "cabelo_curto",
	"cor_cabelo": 2,
	"roupa_cima": "camiseta",
	"cor_roupa_cima": 0,
	"roupa_baixo": "calca",
	"cor_roupa_baixo": 1,
	"calcado": "botinha",
	"chapeu": "",
}

var _sprites := {}
var _cabelo_recortado := false
var _tempo := 0.0
var _caminho := PackedVector2Array()


func _ready() -> void:
	for nome in CAMADAS:
		var sprite := Sprite2D.new()
		sprite.name = nome
		sprite.centered = false
		sprite.offset = DESLOCAMENTO_QUADRO
		add_child(sprite)
		_sprites[nome] = sprite
	atualizar_visual()


func sprite(camada: String) -> Sprite2D:
	return _sprites[camada]


## Troca um item ou cor da aparência e redesenha.
func vestir(chave: String, valor) -> void:
	aparencia[chave] = valor
	atualizar_visual()


func atualizar_visual() -> void:
	if _sprites.is_empty():
		return
	var base := Dados.base_personagem
	_definir_camada("sombra", base.get("sombra"))
	_definir_camada("corpo", base.get("corpo"), Dados.cores_da_paleta("pele", aparencia["pele"]))
	_definir_camada("rosto", base.get("rosto"))

	var chapeu := Dados.item(aparencia["chapeu"])
	var esconde: String = chapeu.get("esconde_cabelo", "nenhum")
	_definir_camada("chapeu", chapeu.get("textura"))

	var cabelo := Dados.item(aparencia["cabelo"]) if esconde != "total" else {}
	var cor_cabelo := Dados.cores_da_paleta("cabelo", aparencia["cor_cabelo"])
	_definir_camada("cabelo_frente", cabelo.get("textura"), cor_cabelo)
	_definir_camada("cabelo_tras", cabelo.get("textura_tras"), cor_cabelo)
	_cabelo_recortado = esconde == "topo"

	for tipo in ["roupa_cima", "roupa_baixo", "calcado"]:
		var item := Dados.item(aparencia[tipo])
		var cores := PackedColorArray()
		if item.get("recoloravel", false):
			cores = Dados.cores_da_paleta("roupa", aparencia.get("cor_" + tipo, 0))
		_definir_camada(tipo, item.get("textura"), cores)
	_atualizar_quadro()


func _definir_camada(camada: String, caminho, cores := PackedColorArray()) -> void:
	var s: Sprite2D = _sprites[camada]
	if caminho == null or caminho == "":
		s.texture = null
		return
	s.texture = load(caminho)
	if camada in CAMADAS_DE_CABECA:
		s.hframes = 3
		s.vframes = int(s.texture.get_height() / 48.0)
	elif camada == "sombra":
		s.hframes = 1
		s.vframes = 1
	else:
		s.hframes = COLUNAS_CORPO
		s.vframes = 3
	if cores.size() == 4:
		var material := s.material as ShaderMaterial
		if material == null:
			material = ShaderMaterial.new()
			material.shader = preload("res://shaders/troca_paleta.gdshader")
			s.material = material
		material.set_shader_parameter("cor_contorno", cores[0])
		material.set_shader_parameter("cor_sombra", cores[1])
		material.set_shader_parameter("cor_base", cores[2])
		material.set_shader_parameter("cor_luz", cores[3])
	else:
		s.material = null


# --- Movimento ------------------------------------------------------------

## Segue uma lista de pontos (em coordenadas do nó pai).
func andar_por(pontos: PackedVector2Array) -> void:
	_caminho = pontos


func esta_andando() -> bool:
	return not _caminho.is_empty()


func _process(delta: float) -> void:
	if _caminho.is_empty():
		_mudar_animacao("parado")
	else:
		var alvo := _caminho[0]
		var falta := alvo - position
		var passo := VELOCIDADE * delta
		if falta.length() <= passo:
			position = alvo
			_caminho.remove_at(0)
			if _caminho.is_empty():
				chegou.emit()
		else:
			position += falta.normalized() * passo
		_olhar_para(falta)
		_mudar_animacao("andar")
	_tempo += delta
	_atualizar_quadro()


func _olhar_para(vetor: Vector2) -> void:
	if vetor.is_zero_approx():
		return
	if absf(vetor.x) > absf(vetor.y):
		direcao = Direcao.LADO
		virado_para_esquerda = vetor.x < 0
	else:
		direcao = Direcao.BAIXO if vetor.y > 0 else Direcao.CIMA


func _mudar_animacao(nova: String) -> void:
	if nova != animacao:
		animacao = nova
		_tempo = 0.0


func _atualizar_quadro() -> void:
	var deslocamentos: Array = Dados.ancoras[animacao]
	var i := int(_tempo * QUADROS_POR_SEGUNDO[animacao]) % deslocamentos.size()
	var coluna: int = PRIMEIRA_COLUNA[animacao] + i
	var ancora := float(deslocamentos[i])
	var espelhar := direcao == Direcao.LADO and virado_para_esquerda
	for camada in CAMADAS:
		var s: Sprite2D = _sprites[camada]
		s.flip_h = espelhar
		if s.texture == null or camada == "sombra":
			continue
		if camada in CAMADAS_DE_CABECA:
			var linha := 1 if camada == "cabelo_frente" and _cabelo_recortado and s.vframes > 1 else 0
			s.frame = linha * 3 + direcao
			s.position.y = ancora
		else:
			s.frame = direcao * COLUNAS_CORPO + coluna
