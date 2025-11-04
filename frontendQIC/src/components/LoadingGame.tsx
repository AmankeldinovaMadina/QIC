import { useEffect, useRef, useState } from 'react';
import oryxImage from '../assets/oryx.png';
import cactusImage from '../assets/cactus.png';

interface LoadingGameProps {
  onComplete?: () => void;
  duration?: number; // in seconds
}

interface Obstacle {
  x: number;
  height: number;
  scored: boolean;
}

export function LoadingGame({ onComplete, duration = 10 }: LoadingGameProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const oryxImageRef = useRef<HTMLImageElement | null>(null);
  const cactusImageRef = useRef<HTMLImageElement | null>(null);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(duration);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const gameStateRef = useRef({
    oryxY: 150,
    oryxVelocity: 0,
    isJumping: false,
    obstacles: [] as Obstacle[],
    gameOver: false,
    score: 0,
    frameCount: 0
  });

  // Load images
  useEffect(() => {
    const oryxImg = new Image();
    const cactusImg = new Image();
    
    let oryxLoaded = false;
    let cactusLoaded = false;
    
    const checkAllLoaded = () => {
      if (oryxLoaded && cactusLoaded) {
        setImagesLoaded(true);
      }
    };
    
    oryxImg.onload = () => {
      oryxLoaded = true;
      checkAllLoaded();
    };
    
    cactusImg.onload = () => {
      cactusLoaded = true;
      checkAllLoaded();
    };
    
    oryxImg.onerror = () => {
      console.error('Failed to load oryx image');
      oryxLoaded = true; // Continue even if image fails
      checkAllLoaded();
    };
    
    cactusImg.onerror = () => {
      console.error('Failed to load cactus image');
      cactusLoaded = true; // Continue even if image fails
      checkAllLoaded();
    };
    
    oryxImg.src = oryxImage;
    cactusImg.src = cactusImage;
    
    oryxImageRef.current = oryxImg;
    cactusImageRef.current = cactusImg;
  }, []);

  useEffect(() => {
    if (!imagesLoaded) return;
    
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Game constants
    const GRAVITY = 0.7;
    const JUMP_STRENGTH = -13;
    const ORYX_WIDTH = 50;
    const ORYX_HEIGHT = 50;
    const GROUND_Y = 170;
    const OBSTACLE_WIDTH = 30;
    const OBSTACLE_HEIGHT = 40;
    const OBSTACLE_SPEED = 6;
    const SPAWN_INTERVAL = 60;

    // Start the game on first interaction
    const startGame = () => {
      if (!gameStarted) {
        setGameStarted(true);
      }
    };

    const handleJump = (e: KeyboardEvent | MouseEvent | TouchEvent) => {
      if (e instanceof KeyboardEvent && e.code !== 'Space') return;
      
      e.preventDefault();
      startGame();
      
      if (!gameStateRef.current.gameOver && gameStateRef.current.oryxY === GROUND_Y) {
        gameStateRef.current.oryxVelocity = JUMP_STRENGTH;
        gameStateRef.current.isJumping = true;
      }
    };

    // Event listeners
    window.addEventListener('keydown', handleJump);
    canvas.addEventListener('click', handleJump);
    canvas.addEventListener('touchstart', handleJump);

    // Countdown timer (only if onComplete is provided)
    let timerInterval: ReturnType<typeof setInterval> | null = null;
    if (onComplete) {
      timerInterval = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            if (timerInterval) clearInterval(timerInterval);
            onComplete();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    // Game loop
    let animationId: number;
    
    const gameLoop = () => {
      if (!ctx) return;
      
      const state = gameStateRef.current;
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw ground
      ctx.fillStyle = '#C4A57B';
      ctx.fillRect(0, GROUND_Y + ORYX_HEIGHT, canvas.width, 30);
      
      // Draw desert dunes/hills in background
      ctx.fillStyle = '#D4B896';
      ctx.beginPath();
      ctx.ellipse(100, GROUND_Y + ORYX_HEIGHT, 80, 20, 0, 0, Math.PI, true);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(250, GROUND_Y + ORYX_HEIGHT, 60, 15, 0, 0, Math.PI, true);
      ctx.fill();
      
      // Update oryx physics
      if (gameStarted && !state.gameOver) {
        state.oryxVelocity += GRAVITY;
        state.oryxY += state.oryxVelocity;
        
        // Ground collision
        if (state.oryxY >= GROUND_Y) {
          state.oryxY = GROUND_Y;
          state.oryxVelocity = 0;
          state.isJumping = false;
        }
      }
      
      // Draw oryx using image
      if (oryxImageRef.current) {
        ctx.drawImage(
          oryxImageRef.current,
          50,
          state.oryxY,
          ORYX_WIDTH,
          ORYX_HEIGHT
        );
      } else {
        // Fallback: draw simple oryx shape
        ctx.fillStyle = '#8B5CF6';
        ctx.fillRect(50, state.oryxY, ORYX_WIDTH, ORYX_HEIGHT);
      }
      
      if (gameStarted && !state.gameOver) {
        // Spawn obstacles
        state.frameCount++;
        if (state.frameCount % SPAWN_INTERVAL === 0) {
          state.obstacles.push({
            x: canvas.width,
            height: OBSTACLE_HEIGHT,
            scored: false
          });
        }
        
        // Update and draw obstacles (cacti)
        state.obstacles = state.obstacles.filter(obstacle => {
          obstacle.x -= OBSTACLE_SPEED;
          
          // Draw cactus using image
          if (cactusImageRef.current) {
            ctx.drawImage(
              cactusImageRef.current,
              obstacle.x,
              GROUND_Y + ORYX_HEIGHT - obstacle.height,
              OBSTACLE_WIDTH,
              obstacle.height
            );
          } else {
            // Fallback: draw simple cactus shape
            ctx.fillStyle = '#228B22';
            ctx.fillRect(obstacle.x, GROUND_Y + ORYX_HEIGHT - obstacle.height, OBSTACLE_WIDTH, obstacle.height);
          }
          
          // Collision detection
          if (
            obstacle.x < 50 + ORYX_WIDTH - 10 &&
            obstacle.x + OBSTACLE_WIDTH - 10 > 50 &&
            state.oryxY + ORYX_HEIGHT - 5 > GROUND_Y + ORYX_HEIGHT - obstacle.height
          ) {
            state.gameOver = true;
            setGameOver(true);
          }
          
          // Score increase - only once per obstacle
          if (!obstacle.scored && obstacle.x + OBSTACLE_WIDTH < 50) {
            obstacle.scored = true;
            state.score++;
            setScore(state.score);
          }
          
          return obstacle.x > -OBSTACLE_WIDTH;
        });
      }
      
      // Draw score on canvas
      ctx.fillStyle = '#333';
      ctx.font = 'bold 24px monospace';
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 4;
      ctx.strokeText(`${state.score}`, 10, 35);
      ctx.fillText(`${state.score}`, 10, 35);
      
      // Game over message
      if (state.gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 80, canvas.width, 60);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 24px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Game Over!', canvas.width / 2, 110);
        ctx.font = '16px sans-serif';
        ctx.fillText('Click or press Space to retry', canvas.width / 2, 135);
        ctx.textAlign = 'left';
      }
      
      animationId = requestAnimationFrame(gameLoop);
    };
    
    gameLoop();

    return () => {
      window.removeEventListener('keydown', handleJump);
      canvas.removeEventListener('click', handleJump);
      canvas.removeEventListener('touchstart', handleJump);
      if (animationId) cancelAnimationFrame(animationId);
      if (timerInterval) clearInterval(timerInterval);
    };
  }, [onComplete, gameStarted, duration, imagesLoaded]);

  const restartGame = () => {
    // Reset game state
    gameStateRef.current = {
      oryxY: 150,
      oryxVelocity: 0,
      isJumping: false,
      obstacles: [],
      gameOver: false,
      score: 0,
      frameCount: 0
    };
    setScore(0);
    setGameOver(false);
    setGameStarted(true);
    setTimeLeft(duration);
    
    // The game loop will automatically restart because gameOver is false
    // and gameStarted is true
  };

  return (
    <div className="flex flex-col items-center justify-center py-4">
      <div className="mb-4 text-center">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">
          {!gameStarted ? 'Oryx Runner' : gameStateRef.current.gameOver ? 'Game Over!' : 'Oryx Runner'}
        </h3>
        <div className="flex items-center justify-center gap-4 text-sm">
          <span className="text-gray-600">Score: <span className="font-bold text-blue-600">{score}</span></span>
          {onComplete && (
            <>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600">Time: <span className="font-bold">{timeLeft}s</span></span>
            </>
          )}
        </div>
        {!gameStarted && (
          <p className="text-xs text-gray-500 mt-2">Press SPACE or tap to jump!</p>
        )}
        {gameStateRef.current.gameOver && (
          <button
            onClick={restartGame}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
          >
            Play Again
          </button>
        )}
      </div>
      
      <div className="relative">
        {!imagesLoaded ? (
          <div className="w-[350px] h-[250px] border-2 border-gray-300 rounded-lg bg-gradient-to-b from-sky-100 to-amber-50 flex items-center justify-center">
            <p className="text-gray-500 text-sm">Loading game...</p>
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            width={350}
            height={250}
            className="border-2 border-gray-300 rounded-lg bg-gradient-to-b from-sky-100 to-amber-50 cursor-pointer"
            style={{
              imageRendering: 'pixelated' as any
            }}
          />
        )}
      </div>

      <p className="mt-4 text-sm text-gray-500">
        {gameStateRef.current.gameOver ? 'Jump to avoid obstacles!' : 'Press SPACE or tap to jump! 🦬'}
      </p>
    </div>
  );
}
