# Este sketch é baseado no post: Wave Collapse Function algorithm in Processing
# Publicado no dia 5 de julho de 2019 no Discourse - Processing Foundation
# https://discourse.processing.org/t/wave-collapse-function-algorithm-in-processing/12983
# Customizado por Monica Rizzolli para gerar output em PDF, salvar png e rodar suave no processing modo Phyton
# Versão: Overlapping model

add_library('pdf')
from collections import Counter
from itertools import chain
from random import choice, sample

out_w, out_h = 60, 60 
f = 12
N = 3

def setup():
    beginRecord(PDF, "nome.pdf")
    size(out_w*f, out_h*f, P2D)
    background(255)
    noStroke()

    global wave, adjacencies, entropy, directions, patterns, freqs, cell_w, cell_h

    img = loadImage('wave10A.png') 
    img_w, img_h = img.width, img.height 
    cell_w, cell_h = width//out_w, height//out_h 
    kernel = tuple(tuple(i + n*img_w for i in xrange(N)) for n in xrange(N)) 
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1)) 
    all = [] 

    for y in xrange(img_h):
        for x in xrange(img_w):
            
            cmat = tuple(tuple(img.pixels[((x+n)%img_w)+(((a[0]+img_w*y)/img_w)%img_h)*img_w] for n in a) for a in kernel)
            
            # Padrões rotacionados (90°, 180°, 270°, 360°)
            for r in xrange(4):
                cmat = zip(*cmat[::-1]) # +90°
                all.append(cmat)
                all.append(cmat[::-1]) # reflexão vertical 
                all.append([a[::-1] for a in cmat]) # reflexão horizontal 


    all = [tuple(chain.from_iterable(p)) for p in all]
    c = Counter(all) 
    freqs = c.values() 
    patterns = c.keys() 
    npat = len(freqs) 

    wave = dict(enumerate(tuple(set(range(npat)) for i in xrange(out_w*out_h))))

    entropy = dict(enumerate(sample(tuple(npat if i > 0 else npat-1 for i in xrange(out_w*out_h)), out_w*out_h)))

    adjacencies = dict(enumerate(tuple(set() for dir in xrange(len(directions))) for i in xrange(npat))) # explanations below

    '''
    0 = esquerda
    1 = direita
    2 = em cima
    3 = em baixo
    '''
    
    for i1 in xrange(npat):
        for i2 in xrange(npat):

            if [n for i, n in enumerate(patterns[i1]) if i%N!=(N-1)] == [n for i, n in enumerate(patterns[i2]) if i%N!=0]:
                adjacencies[i1][0].add(i2)
                adjacencies[i2][1].add(i1)

            if patterns[i1][:(N*N)-N] == patterns[i2][N:]:
                adjacencies[i1][2].add(i2)
                adjacencies[i2][3].add(i1)

def draw():
    global entropy, wave, tecla
    print(frameCount)

    if not entropy:
        endRecord()
        print 'finished'
        noLoop()
        return

    entropy_min = min(entropy, key = entropy.get)

    pattern_id = choice([pattern_idx for pattern_idx in wave[entropy_min] for i in xrange(freqs[pattern_idx])]) 

    wave[entropy_min] = {pattern_id}

    del entropy[entropy_min]

    stack = {entropy_min}

    while stack:

        cell_idx = stack.pop() # index of current cell
        for dir, t in enumerate(directions):
            x = (cell_idx%out_w + t[0])%out_w
            y = (cell_idx/out_w + t[1])%out_h
            neighbor_idx = x + y * out_w # index of negihboring cell

            if neighbor_idx in entropy:

                possible = {n for pattern_idx in wave[cell_idx] for n in adjacencies[pattern_idx][dir]}

                available = wave[neighbor_idx]

                if not available.issubset(possible):

                    intersection = possible & available

                    if not intersection:
                        print 'contradiction'
                        noLoop()
                        return

                    wave[neighbor_idx] = intersection

                    entropy[neighbor_idx] = len(wave[neighbor_idx]) - random(.1)

                    stack.add(neighbor_idx)

    fill(patterns[pattern_id][0])
    rect((entropy_min%out_w) * cell_w, (entropy_min/out_w) * cell_h, cell_w, cell_h)

    saveFrame("#######waveCF.png")
    
