// Variables globales
let currentSlide = 1;
const totalSlides = 15;

// Elementos del DOM
const slidesContainer = document.getElementById('slidesContainer');
const slideNumber = document.getElementById('slideNumber');
const progressFill = document.getElementById('progressFill');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    updateSlideDisplay();
    setupEventListeners();
    setupKeyboardNavigation();
    setupTouchNavigation();
    startAutoProgress();
});

// Event listeners
function setupEventListeners() {
    prevBtn.addEventListener('click', () => changeSlide(-1));
    nextBtn.addEventListener('click', () => changeSlide(1));
}

// Navegación con teclado
function setupKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        switch(e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                changeSlide(-1);
                break;
            case 'ArrowRight':
                e.preventDefault();
                changeSlide(1);
                break;
            case ' ':
                e.preventDefault();
                changeSlide(1);
                break;
            case 'Home':
                e.preventDefault();
                goToSlide(1);
                break;
            case 'End':
                e.preventDefault();
                goToSlide(totalSlides);
                break;
        }
    });
}

// Navegación táctil
function setupTouchNavigation() {
    let touchStartX = 0;
    let touchEndX = 0;

    slidesContainer.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    slidesContainer.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                changeSlide(1); // Swipe left - next slide
            } else {
                changeSlide(-1); // Swipe right - previous slide
            }
        }
    }
}

// Cambiar slide
function changeSlide(direction) {
    const newSlide = currentSlide + direction;
    
    if (newSlide >= 1 && newSlide <= totalSlides) {
        goToSlide(newSlide);
    }
}

// Ir a slide específico
function goToSlide(slideNum) {
    if (slideNum < 1 || slideNum > totalSlides) return;
    
    // Remover clase active del slide actual
    const currentSlideElement = document.querySelector(`[data-slide="${currentSlide}"]`);
    if (currentSlideElement) {
        currentSlideElement.classList.remove('active');
        currentSlideElement.classList.add('prev');
    }
    
    // Actualizar número de slide
    currentSlide = slideNum;
    
    // Agregar clase active al nuevo slide
    setTimeout(() => {
        // Remover prev de todos los slides
        document.querySelectorAll('.slide').forEach(slide => {
            slide.classList.remove('prev');
        });
        
        const newSlideElement = document.querySelector(`[data-slide="${currentSlide}"]`);
        if (newSlideElement) {
            newSlideElement.classList.add('active');
        }
        
        updateSlideDisplay();
        triggerSlideAnimations();
    }, 100);
}

// Actualizar display
function updateSlideDisplay() {
    // Actualizar número de slide
    slideNumber.textContent = `${currentSlide} / ${totalSlides}`;
    
    // Actualizar barra de progreso
    const progress = (currentSlide / totalSlides) * 100;
    progressFill.style.width = `${progress}%`;
    
    // Actualizar estado de botones
    prevBtn.disabled = currentSlide === 1;
    nextBtn.disabled = currentSlide === totalSlides;
    
    // Actualizar URL sin recargar
    history.replaceState(null, null, `#slide${currentSlide}`);
}

// Animaciones específicas por slide
function triggerSlideAnimations() {
    const activeSlide = document.querySelector('.slide.active');
    if (!activeSlide) return;
    
    // Reset animaciones
    const animatedElements = activeSlide.querySelectorAll('.concept-card, .agent-card, .benefit-card, .use-case-card');
    animatedElements.forEach((el, index) => {
        el.style.animation = 'none';
        el.offsetHeight; // Trigger reflow
        el.style.animation = `slideIn 0.6s ease ${index * 0.1}s both`;
    });
    
    // Animaciones específicas por tipo de slide
    const slideData = activeSlide.getAttribute('data-slide');
    
    switch(slideData) {
        case '3': // Arquitectura
            animateArchitectureLayers();
            break;
        case '5': // RAG
            animateRAGFlow();
            break;
        case '6': // Workflow
            animateWorkflowSteps();
            break;
        case '9': // Comunicación
            animateCommunicationFlow();
            break;
        case '10': // ChromaDB
            animateVectorSimilarity();
            break;
    }
}

// Animación de capas de arquitectura
function animateArchitectureLayers() {
    const layers = document.querySelectorAll('.layer');
    layers.forEach((layer, index) => {
        layer.style.transform = 'translateX(-100px)';
        layer.style.opacity = '0';
        
        setTimeout(() => {
            layer.style.transition = 'all 0.6s ease';
            layer.style.transform = 'translateX(0)';
            layer.style.opacity = '1';
        }, index * 200);
    });
}

// Animación de flujo RAG
function animateRAGFlow() {
    const steps = document.querySelectorAll('.rag-step');
    const arrows = document.querySelectorAll('.arrow');
    
    steps.forEach((step, index) => {
        step.style.transform = 'scale(0.8)';
        step.style.opacity = '0';
        
        setTimeout(() => {
            step.style.transition = 'all 0.5s ease';
            step.style.transform = 'scale(1)';
            step.style.opacity = '1';
        }, index * 300);
    });
    
    arrows.forEach((arrow, index) => {
        arrow.style.opacity = '0';
        setTimeout(() => {
            arrow.style.transition = 'opacity 0.3s ease';
            arrow.style.opacity = '1';
        }, (index + 1) * 300 + 150);
    });
}

// Animación de pasos de workflow
function animateWorkflowSteps() {
    const steps = document.querySelectorAll('.workflow-step');
    steps.forEach((step, index) => {
        step.style.transform = 'translateY(30px)';
        step.style.opacity = '0';
        
        setTimeout(() => {
            step.style.transition = 'all 0.5s ease';
            step.style.transform = 'translateY(0)';
            step.style.opacity = '1';
        }, index * 200);
    });
}

// Animación de flujo de comunicación
function animateCommunicationFlow() {
    const agents = document.querySelectorAll('.agent-comm');
    const arrows = document.querySelectorAll('.arrow-right');
    
    agents.forEach((agent, index) => {
        agent.style.transform = 'scale(0.9)';
        agent.style.opacity = '0';
        
        setTimeout(() => {
            agent.style.transition = 'all 0.5s ease';
            agent.style.transform = 'scale(1)';
            agent.style.opacity = '1';
        }, index * 400);
    });
    
    arrows.forEach((arrow, index) => {
        arrow.style.opacity = '0';
        setTimeout(() => {
            arrow.style.transition = 'opacity 0.3s ease';
            arrow.style.opacity = '1';
        }, (index + 1) * 400 + 200);
    });
}

// Animación de similitud de vectores
function animateVectorSimilarity() {
    const docResults = document.querySelectorAll('.doc-result');
    docResults.forEach((result, index) => {
        result.style.transform = 'translateX(-20px)';
        result.style.opacity = '0';
        
        setTimeout(() => {
            result.style.transition = 'all 0.4s ease';
            result.style.transform = 'translateX(0)';
            result.style.opacity = '1';
        }, index * 150);
    });
}

// Auto-progreso suave para elementos animados
function startAutoProgress() {
    // Agregar efecto de hover mejorado para cards
    const cards = document.querySelectorAll('.concept-card, .agent-card, .benefit-card, .use-case-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 15px 35px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
    });
}

// Manejar navegación por URL
window.addEventListener('popstate', function() {
    const hash = window.location.hash;
    if (hash.startsWith('#slide')) {
        const slideNum = parseInt(hash.replace('#slide', ''));
        if (slideNum >= 1 && slideNum <= totalSlides) {
            goToSlide(slideNum);
        }
    }
});

// Cargar slide inicial desde URL
window.addEventListener('load', function() {
    const hash = window.location.hash;
    if (hash.startsWith('#slide')) {
        const slideNum = parseInt(hash.replace('#slide', ''));
        if (slideNum >= 1 && slideNum <= totalSlides) {
            goToSlide(slideNum);
        }
    }
});

// Funciones de utilidad para demostración
function highlightCode() {
    // Resaltar sintaxis de código si Prism está disponible
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

// Efectos especiales para slides específicos
function addSpecialEffects() {
    // Efecto de escritura para el slide de título
    const titleSlide = document.querySelector('[data-slide="1"]');
    if (titleSlide && currentSlide === 1) {
        const title = titleSlide.querySelector('h1');
        if (title) {
            title.style.opacity = '0';
            setTimeout(() => {
                title.style.transition = 'opacity 1s ease';
                title.style.opacity = '1';
            }, 500);
        }
    }
}

// Demo interactiva para el slide de RAG
function setupRAGDemo() {
    const ragSlide = document.querySelector('[data-slide="5"]');
    if (ragSlide) {
        const steps = ragSlide.querySelectorAll('.rag-step');
        steps.forEach((step, index) => {
            step.addEventListener('click', function() {
                // Resaltar el paso seleccionado
                steps.forEach(s => s.classList.remove('highlighted'));
                this.classList.add('highlighted');
                
                // Mostrar información adicional
                showStepDetails(index);
            });
        });
    }
}

function showStepDetails(stepIndex) {
    const details = [
        "Procesamiento: Los PDFs se dividen en chunks de texto manejables",
        "Embeddings: Cada chunk se convierte en un vector de 384 dimensiones",
        "ChromaDB: Los vectores se almacenan con metadatos para búsqueda eficiente",
        "Búsqueda: Se encuentra contenido similar usando distancia coseno",
        "Generación: El LLM usa el contexto recuperado para generar respuestas precisas"
    ];
    
    // Crear tooltip o modal con la información
    console.log(`Paso ${stepIndex + 1}: ${details[stepIndex]}`);
}

// Navegación mejorada con indicadores visuales
function enhanceNavigation() {
    // Agregar indicadores de slide
    const nav = document.querySelector('.navigation');
    const slideIndicators = document.createElement('div');
    slideIndicators.className = 'slide-indicators';
    
    for (let i = 1; i <= totalSlides; i++) {
        const indicator = document.createElement('button');
        indicator.className = 'slide-indicator';
        indicator.setAttribute('data-slide', i);
        indicator.addEventListener('click', () => goToSlide(i));
        slideIndicators.appendChild(indicator);
    }
    
    nav.appendChild(slideIndicators);
    updateIndicators();
}

function updateIndicators() {
    const indicators = document.querySelectorAll('.slide-indicator');
    indicators.forEach((indicator, index) => {
        if (index + 1 === currentSlide) {
            indicator.classList.add('active');
        } else {
            indicator.classList.remove('active');
        }
    });
}

// Función para presentación en pantalla completa
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(console.error);
    } else {
        document.exitFullscreen();
    }
}

// Agregar controles adicionales
document.addEventListener('keydown', function(e) {
    if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        toggleFullscreen();
    }
});

// Inicializar características adicionales
setTimeout(() => {
    highlightCode();
    setupRAGDemo();
    addSpecialEffects();
}, 1000);
