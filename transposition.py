import re

TPRE = re.compile(r'[ ]*\[%tp ([^\]]*)\]') # permet la recherche
TLRE = re.compile(r'[ ]*\[%tl ([^\]]*)\]') # multiple efficace

# format des tags pour les transpositions :
# [%tp num_p s1 s2 ...] (primaire, rattachée à ses secondaires)
# [%tl num_s p] (secondaire, rattachée à sa primaire)

# re.findall(r'\[%tp ([^\]]*)\]',pgn.comment) -> texte dans le [%tp ...]
# re.search(r'\[%tp ([^\]]*)\]',pgn.comment)[1] -> idem
# TPRE.search(pgn.comment)[1] -> idem et plus efficace

# déplacer les coups et commentaires du nœud vers la transposition primaire
# de manière récursive

# /!\ si des transpositions sont supprimées...

noeud_transposition = {} # { int : noeud}
transpositions_secondaires = {} # { int : int list} clés primaires valeurs secondaires
transposition_primaire = {} # { int : int } clés secondaires valeur primaire

def get_new_node_number():
    n=1
    while n in noeud_transposition:
        n+=1
    return n

def check_comment_primary(pgn):
    if TPRE.search(pgn.comment):
        return True
    else:
        return False
    
def get_comment_primary(pgn):
    return list(map(int,TPRE.search(pgn.comment)[1].split()))

def set_primary_new(pgn):
    n = get_new_node_number()
    noeud_transposition[n] = pgn
    transpositions_secondaires[n]=[]
    pgn.comment = pgn.comment + f" [%tp {n}]"
    
def check_primary(pgn):
    for p,n in noeud_transposition.items():
        if n is pgn:
            return p in transpositions_secondaires
    return False

def isolate_primary(pgn):
    p = get_number_from_node(pgn)
    return transpositions_secondaires[p] == []

def add_secondary_comment(p,s):
    pgn = noeud_transposition[p]
    comment = TPRE.sub('',pgn.comment)
    pgn.comment = comment + f" [%tp {" ".join(map(str,[p]+transpositions_secondaires[p]))}]"

def check_comment_secondary(pgn):
    if TLRE.search(pgn.comment):
        return True
    else:
        return False
    
def get_comment_secondary(pgn):
    return tuple(map(int,TLRE.search(pgn.comment)[1].split()))

def check_secondary(pgn):
    for p,n in noeud_transposition.items():
        if n is pgn:
            return p in transposition_primaire
    return False

def set_secondary(pgn,s,p):
    noeud_transposition[s] = pgn
    transpositions_secondaires[p].append(s)
    transposition_primaire[s] = p

def set_secondary_new(pgn,p):
    s = get_new_node_number()
    set_secondary(pgn,s,p)
    pgn.comment = pgn.comment + f"[%tl {s} {p}]"
    add_secondary_comment(p,s)

def update_secondary_comment(s):
    pgn = noeud_transposition[s]
    p = transposition_primaire[s]
    comment = TLRE.sub('',pgn.comment)
    pgn.comment = comment + f"[%tl {s} {p}]"

def remove_secondary(s):
    pgn = noeud_transposition[s]
    del noeud_transposition[s]
    del transposition_primaire[s]
    pgn.comment = TLRE.sub('',pgn.comment)

def get_number_from_node(pgn):
    for num,node in noeud_transposition.items():
        if node is pgn:
            return num
    return None


def check_transposition(pgn):
    return check_primary(pgn) or check_secondary(pgn)

def make_primary(pgn):
    assert not check_comment_primary(pgn)
    set_primary_new(pgn)

def remove_primary(pgn):
    assert check_primary(pgn)
    p = get_number_from_node(pgn)
    sl = transpositions_secondaires[p]
    del transpositions_secondaires[p]
    del noeud_transposition[p]
    pgn.comment = TPRE.sub('',pgn.comment)
    for s in sl:
        remove_secondary(s)

def exchange_with_primary(pgn):
    assert check_secondary(pgn)
    s = get_number_from_node(pgn)
    p = transposition_primaire[s]
    sl = transpositions_secondaires[p]

    for i,o in enumerate(sl):
        if o == s:
            mem = i
        else:
            transposition_primaire[o]=s
            update_secondary_comment(o)
    sl[mem]=p
    del transposition_primaire[s]
    del transpositions_secondaires[p]
    transposition_primaire[p]=s
    transpositions_secondaires[s]=sl
    pgn_p = noeud_transposition[p]
    transfert(pgn_p,pgn)
    pgn_p.comment = f"[%tl {p} {s}]"
    comment = TPRE.sub('',pgn.comment)
    pgn.comment = comment + f" [%tp {" ".join(map(str,[s]+transpositions_secondaires[s]))}]"

def link(pgn):
    '''
    Searches for a primary transposition corresponding
    if found, actual position becomes secondary transposition
    '''
    assert not check_comment_secondary(pgn)
    fen = pgn.board().fen()
    for p in transpositions_secondaires:
        if noeud_transposition[p].board().fen() == fen:
            set_secondary_new(pgn,p)
            break
    comment = TLRE.sub('',pgn.comment)
    if pgn.variations != [] or comment !='':
        pgn_p = noeud_transposition[p]
        transfert(pgn, pgn_p)

def after(pgn):
    if check_primary(pgn):
        p = get_number_from_node(pgn)
        if transpositions_secondaires[p] != []:
            s = transpositions_secondaires[p][0]
            return noeud_transposition[s]
    elif check_secondary(pgn):
        s = get_number_from_node(pgn)
        p = transposition_primaire[s]
        sl = transpositions_secondaires[p]
        i = sl.index(s)+1
        n = (sl+[p])[i]
        return noeud_transposition[n]

def get_primary_from_secondary_node(pgn):
    if check_secondary(pgn):
        return noeud_transposition[transposition_primaire[get_number_from_node(pgn)]]
    else:
        return pgn

def recursive_copy(initial,final):
    # Tests selon primaire/secondaire ?
    # Il faut redonner les bons noeuds s’ils sont refaits
    # Et attention aux commentaires... un noeud ne peut pas être plusieurs transpositions
    final.comment += initial.comment
    for child in initial.variations:
        move = child.move
        if not final.has_variation(move):
            child_final = final.add_variation(move)
            recursive_copy(child,child_final)
        else:
            child_final = final.variation(move)
            recursive_copy(child,child_final)
        if check_transposition(child):
            s = get_number_from_node(child)
            noeud_transposition[s]=child_final
            

def transfert(initial,final):
    assert check_secondary(initial)
    assert check_primary(final)
    initial.comment = TLRE.sub('',initial.comment)
    recursive_copy(initial,final)
    s = get_number_from_node(initial)
    p = get_number_from_node(final)
    initial.comment = f"[%tl {s} {p}]"
    initial.variations = []

def check_all(pgn):
    '''
    lit le PGN et remplit les variables de transposition par rapport aux commentaires
    '''
    file = [pgn.game()] # parcours en largeur depuis la racine
    while file != []:
        node = file.pop(0)
        if check_comment_primary(node):
            p,*liste = get_comment_primary(node)
            noeud_transposition[p]=node
            transpositions_secondaires[p]=liste
        elif check_comment_secondary(node):
            s,p = get_comment_secondary(node)
            noeud_transposition[s]=node
            transposition_primaire[s]=p
        file.extend(node.variations)

    # Maintenant :
    # on assure que les noeuds secondaires n’ont pas de fils
    # même si le fichier importé ne satisfait pas cela
    # S’ils en ont, on les transfère vers le principal
    for s,p in transposition_primaire.items():
        pgn_s = noeud_transposition[s]
        comment = TLRE.sub('',pgn_s.comment)
        if pgn_s.variations != [] or comment !='':
            pgn_p = noeud_transposition[p]
            transfert(pgn_s, pgn_p)

def init(pgn):
    global noeud_transposition, transpositions_secondaires, transposition_primaire
    noeud_transposition = {}
    transpositions_secondaires = {}
    transposition_primaire = {}
    check_all(pgn)
    
def check_auto_all(pgn):
    '''
    lit le PGN et cherche automatiquement les transpositions, indiquées ou non
    Se charge de créer une principale en lui associant tous les coups trouvés
    dans les secondaires, et modifie donc le PGN
    '''
    pass