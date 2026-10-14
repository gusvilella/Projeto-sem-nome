class_name Personagem
extends Node2D
## Personagem montado em camadas (paper doll).
## Ver docs/gdd/05-direcao-de-arte.md#personagem-em-camadas-paper-doll.

signal chegou

enum Direcao { BAIXO, CIMA, LADO }

const NOMES_DIRECAO := ["baixo", "cima", "lado"]
const VELOCIDADE := 72.0
const QUADROS_POR_SEGUNDO := {"parado": 2.0, "andar": 8.0}
const COLUNAS_CORPO := 6
## Para trocar entre andar de lado e de frente/costas, um eixo precisa
## dominar o outro por esta proporção (evita piscar em diagonais).
const HISTERESE := 1.35

## Ordem de desenho, de baixo para cima.
const CAMADAS := [
	"sombra", "cabelo_tras", "corpo", "rosto", "roupa_baixo",
	"calcado", "roupa_cima", "cabelo_frente", "chapeu",
]
## Camadas desenhadas uma vez por direção, posicionadas pela âncora de cabeça.
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
	## Personagem inteiro, sem camadas (ex.: gerado por IA). Vazio = usar as camadas.
	"completo": "",
}

var _sprites := {}
var _cabelo_recortado := false
var _tempo := 0.0
var _caminho := PackedVector2Array()
var _pes := Vector2.ZERO
var _ponto_cabeca := Vector2.ZERO
var _altura_cabeca := 0


func _ready() -> void:
	_pes = Dados.vetor(Dados.ancoras["pes"])
	_ponto_cabeca = Dados.vetor(Dados.ancoras["ponto_cabeca"])
	_altura_cabeca = int(Dados.ancoras["quadro_cabeca"][1])
	for nome in CAMADAS:
		var s := Sprite2D.new()
		s.name = nome
		s.centered = false
		s.offset = -_ponto_cabeca if nome in CAMADAS_DE_CABECA else -_pes
		add_child(s)
		_sprites[nome] = s
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
	var completo := Dados.item(aparencia.get("completo", ""))
	if not completo.is_empty():
		for camada in CAMADAS:
			if camada != "sombra":
				_definir_camada(camada, null)
		_definir_camada("corpo", completo["textura"])
		_cabelo_recortado = false
		_atualizar_quadro()
		return
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
		s.vframes = maxi(1, roundi(s.texture.get_height() / float(_altura_cabeca)))
	elif camada == "sombra":
		s.hframes = 1
		s.vframes = 1
	else:
		s.hframes = COLUNAS_CORPO
		s.vframes = 3
	if cores.size() == 8:
		var material := s.material as ShaderMaterial
		if material == null:
			material = ShaderMaterial.new()
			material.shader = preload("res://shaders/troca_paleta.gdshader")
			s.material = material
		material.set_shader_parameter("cores", cores)
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
	var ax := absf(vetor.x)
	var ay := absf(vetor.y)
	var de_lado := direcao == Direcao.LADO
	if animacao == "parado":
		de_lado = ax > ay
	elif de_lado and ay > ax * HISTERESE:
		de_lado = false
	elif not de_lado and ax > ay * HISTERESE:
		de_lado = true
	if de_lado:
		direcao = Direcao.LADO
		virado_para_esquerda = vetor.x < 0
	else:
		direcao = Direcao.BAIXO if vetor.y > 0 else Direcao.CIMA


func _mudar_animacao(nova: String) -> void:
	if nova != animacao:
		animacao = nova
		_tempo = 0.0


func _atualizar_quadro() -> void:
	var colunas: Array = Dados.ancoras["colunas"][animacao]
	var i := int(_tempo * QUADROS_POR_SEGUNDO[animacao]) % colunas.size()
	var coluna := int(colunas[i])
	var ancora := Dados.vetor(Dados.ancoras["cabeca"][NOMES_DIRECAO[direcao]][coluna]) - _pes
	var espelhar := direcao == Direcao.LADO and virado_para_esquerda
	if espelhar:
		ancora.x = -ancora.x
	for camada in CAMADAS:
		var s: Sprite2D = _sprites[camada]
		s.flip_h = espelhar
		if s.texture == null or camada == "sombra":
			continue
		if camada in CAMADAS_DE_CABECA:
			var linha := 1 if camada == "cabelo_frente" and _cabelo_recortado and s.vframes > 1 else 0
			s.frame = linha * 3 + direcao
			s.position = ancora
		else:
			s.frame = direcao * COLUNAS_CORPO + coluna
