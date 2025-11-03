import { Sparkles, Plane, MapPin, Calendar } from 'lucide-react';
import { motion } from 'motion/react';

interface TripGeneratingPageProps {
  destination?: string;
}

export function TripGeneratingPage({ destination }: TripGeneratingPageProps) {
  return (
    <div className="max-w-md mx-auto min-h-screen bg-gradient-to-b from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center px-6">
      <div className="text-center">
        {/* Animated Qico Avatar */}
        <motion.div
          className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-2xl"
          animate={{
            scale: [1, 1.1, 1],
            rotate: [0, 5, -5, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <Sparkles className="w-12 h-12 text-white" />
        </motion.div>

        {/* Main Text */}
        <motion.h2
          className="text-2xl font-semibold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          Creating Your Perfect Trip
        </motion.h2>
        
        <motion.p
          className="text-gray-600 mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {destination ? `Planning your adventure to ${destination}...` : 'Qico is crafting your personalized itinerary...'}
        </motion.p>

        {/* Animated Icons */}
        <div className="flex justify-center gap-4 mb-8">
          <motion.div
            className="w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center"
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0
            }}
          >
            <Plane className="w-6 h-6 text-blue-600" />
          </motion.div>
          
          <motion.div
            className="w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center"
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.3
            }}
          >
            <MapPin className="w-6 h-6 text-purple-600" />
          </motion.div>
          
          <motion.div
            className="w-12 h-12 rounded-full bg-white shadow-lg flex items-center justify-center"
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.6
            }}
          >
            <Calendar className="w-6 h-6 text-pink-600" />
          </motion.div>
        </div>

        {/* Loading Dots */}
        <div className="flex justify-center gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.2
              }}
            />
          ))}
        </div>

        {/* Progress Text */}
        <motion.div
          className="mt-8 space-y-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <motion.p
            className="text-sm text-gray-500"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            Analyzing your preferences...
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
