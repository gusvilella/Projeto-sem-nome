class_name PainelPrototipo
extends CanvasLayer
## Painel de testes da Fase 0: controla a vida da região e troca a aparência do
## personagem (um "provador"). Não é a interface final do jogo.

const COR_MADEIRA := Color("5b3a29")
const COR_MADEIRA_CLARA := Color("8a5a3c")
const COR_BORDA := Color("3a241a")
const COR_TEXTO := Color("fcecc8")

## [rótulo, chave da aparência, origem da lista ("paleta:<grupo>" ou "item:<tipo>")]
const OPCOES := [
	["Pele", "pele", "paleta:pele"],
	["Cabelo", "cabelo", "item:cabelo"],
	["Cor do cabelo", "cor_cabelo", "paleta:cabelo"],
	["Roupa", "roupa_cima", "item:roupa_cima"],
	["Cor da roupa", "cor_roupa_cima", "paleta:roupa"],
	["Cor da calça", "cor_roupa_baixo", "paleta:roupa"],
	["Chapéu", "chapeu", "item:chapeu"],
]

var vale: Vale
var personagem: Personagem
var slider: HSlider
var provador: PanelContainer

var _rotulo_vida: Label
var _rotulo_marco: Label
var _aviso: Label
var _valores := {}


func configurar(v: Vale, p: Personagem) -> void:
	vale = v
	personagem = p
	_construir()
	vale.marco_alcancado.connect(_ao_alcancar_marco)
	_atualizar_textos()


func _construir() -> void:
	var raiz := Control.new()
	raiz.set_anchors_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.theme = _criar_tema()
	add_child(raiz)

	# Topo: vida da região
	var topo := PanelContainer.new()
	topo.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE, Control.PRESET_MODE_MINSIZE, 4)
	raiz.add_child(topo)
	var caixa := VBoxContainer.new()
	topo.add_child(caixa)
	_rotulo_vida = Label.new()
	caixa.add_child(_rotulo_vida)
	slider = HSlider.new()
	slider.max_value = 100
	slider.step = 1
	slider.value_changed.connect(_ao_mudar_vida)
	caixa.add_child(slider)
	_rotulo_marco = Label.new()
	_rotulo_marco.add_theme_font_size_override("font_size", 9)
	caixa.add_child(_rotulo_marco)

	# Aviso de marco alcançado
	_aviso = Label.new()
	_aviso.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_aviso.position.y = 96
	_aviso.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_aviso.add_theme_color_override("font_outline_color", COR_BORDA)
	_aviso.add_theme_constant_override("outline_size", 4)
	_aviso.modulate.a = 0.0
	raiz.add_child(_aviso)

	# Base: provador
	var base := VBoxContainer.new()
	base.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE, Control.PRESET_MODE_MINSIZE, 4)
	base.grow_vertical = Control.GROW_DIRECTION_BEGIN
	base.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(base)

	var alternar := Button.new()
	alternar.text = "Provador"
	alternar.toggle_mode = true
	alternar.button_pressed = true
	alternar.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	base.add_child(alternar)

	provador = PanelContainer.new()
	alternar.toggled.connect(provador.set_visible)
	base.add_child(provador)
	var grade := GridContainer.new()
	grade.columns = 4
	provador.add_child(grade)
	for opcao in OPCOES:
		var nome := Label.new()
		nome.text = opcao[0]
		nome.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		grade.add_child(nome)
		var anterior := Button.new()
		anterior.text = " < "
		anterior.pressed.connect(trocar.bind(opcao[1], -1))
		grade.add_child(anterior)
		var valor := Label.new()
		valor.custom_minimum_size.x = 120
		valor.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		grade.add_child(valor)
		_valores[opcao[1]] = valor
		var proximo := Button.new()
		proximo.text = " > "
		proximo.pressed.connect(trocar.bind(opcao[1], 1))
		grade.add_child(proximo)


func _criar_tema() -> Theme:
	var tema := Theme.new()
	tema.default_font_size = 11
	tema.set_color("font_color", "Label", COR_TEXTO)
	tema.set_color("font_color", "Button", COR_TEXTO)
	tema.set_color("font_pressed_color", "Button", COR_TEXTO)
	tema.set_color("font_hover_color", "Button", Color.WHITE)
	tema.set_stylebox("panel", "PanelContainer", _caixa(COR_MADEIRA, 6))
	tema.set_stylebox("normal", "Button", _caixa(COR_MADEIRA_CLARA, 3))
	tema.set_stylebox("hover", "Button", _caixa(COR_MADEIRA_CLARA.lightened(0.12), 3))
	tema.set_stylebox("pressed", "Button", _caixa(COR_MADEIRA_CLARA.darkened(0.2), 3))
	tema.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	return tema


func _caixa(cor: Color, margem: int) -> StyleBoxFlat:
	var caixa := StyleBoxFlat.new()
	caixa.bg_color = cor
	caixa.border_color = COR_BORDA
	caixa.set_border_width_all(2)
	caixa.set_corner_radius_all(3)
	caixa.set_content_margin_all(margem)
	return caixa


## Lista de valores possíveis para uma opção do provador: [[valor, nome], ...]
func valores_da_opcao(chave: String) -> Array:
	var origem: String = ""
	for opcao in OPCOES:
		if opcao[1] == chave:
			origem = opcao[2]
	var partes := origem.split(":")
	var lista := []
	if partes[0] == "paleta":
		var paletas := Dados.lista_paletas(partes[1])
		for i in paletas.size():
			lista.append([i, paletas[i]["nome"]])
	else:
		if partes[1] == "chapeu":
			lista.append(["", "Nenhum"])
		for item in Dados.itens_do_tipo(partes[1]):
			lista.append([item["id"], item["nome"]])
	return lista


func trocar(chave: String, passo: int) -> void:
	var lista := valores_da_opcao(chave)
	var atual := 0
	for i in lista.size():
		if lista[i][0] == personagem.aparencia[chave]:
			atual = i
	personagem.vestir(chave, lista[wrapi(atual + passo, 0, lista.size())][0])
	_atualizar_textos()


func _ao_mudar_vida(valor: float) -> void:
	vale.definir_vida(valor)
	_atualizar_textos()


func _atualizar_textos() -> void:
	_rotulo_vida.text = "Vida da %s: %d%%" % [vale.regiao["nome"], vale.vida]
	var marco := vale.proximo_marco()
	if marco.is_empty():
		_rotulo_marco.text = "Todos os marcos alcançados!"
	else:
		_rotulo_marco.text = "Próximo marco: %d%% · %s" % [marco["vida"], marco["descricao"]]
	for chave in _valores:
		for par in valores_da_opcao(chave):
			if par[0] == personagem.aparencia[chave]:
				_valores[chave].text = par[1]


func _ao_alcancar_marco(marco: Dictionary) -> void:
	_aviso.text = marco["descricao"]
	_aviso.reset_size()
	_aviso.position.x = (_aviso.get_parent_control().size.x - _aviso.size.x) / 2.0
	var tween := create_tween()
	tween.tween_property(_aviso, "modulate:a", 1.0, 0.3)
	tween.tween_interval(1.8)
	tween.tween_property(_aviso, "modulate:a", 0.0, 0.6)
