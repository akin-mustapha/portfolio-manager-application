import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Icon } from './icons';
import {
  motionConfigs,
  glassStyles,
  gradientStyles,
  hoverStyles,
  createCardStyles,
  createButtonStyles,
  staggerConfigs,
  cn,
  type AnimationStyle,
} from '../utils';

const AnimationDemo: React.FC = () => {
  const [selectedAnimation, setSelectedAnimation] = useState<AnimationStyle>('from-bottom');
  const [showCards, setShowCards] = useState(true);

  const animationStyles: AnimationStyle[] = [
    'from-bottom',
    'from-top',
    'from-left',
    'from-right',
    'from-center',
    'fade',
    'scale',
    'bounce',
  ];

  const demoCards = [
    { title: 'Total Value', value: '$125,430.50', change: '+5.2%', positive: true },
    { title: 'Total Return', value: '$25,430.50', change: '+25.4%', positive: true },
    { title: 'Today\'s Change', value: '-$1,234.56', change: '-0.98%', positive: false },
    { title: 'Dividend Yield', value: '3.2%', change: '+0.1%', positive: true },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          className={cn(createCardStyles('glass'), 'text-center')}
          {...motionConfigs.card}
        >
          <h1 className="text-3xl font-bold text-white mb-2">
            Animation System Demo
          </h1>
          <p className="text-gray-300">
            Modern UI foundation with Framer Motion and Tailwind CSS
          </p>
        </motion.div>

        {/* Animation Controls */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Animation Controls
          </h2>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {animationStyles.map((style) => (
              <button
                key={style}
                onClick={() => setSelectedAnimation(style)}
                className={cn(
                  createButtonStyles(
                    selectedAnimation === style ? 'primary' : 'secondary',
                    'sm'
                  )
                )}
              >
                {style}
              </button>
            ))}
          </div>
          
          <button
            onClick={() => setShowCards(!showCards)}
            className={cn(createButtonStyles('primary', 'md'))}
          >
            {showCards ? 'Hide Cards' : 'Show Cards'}
          </button>
        </motion.div>

        {/* Glass Morphism Examples */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Glass Morphism Styles
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(glassStyles).map(([key, className]) => (
              <motion.div
                key={key}
                className={cn(className, 'p-4 rounded-lg')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <h3 className="font-medium text-white capitalize">{key}</h3>
                <p className="text-sm text-gray-300 mt-1">
                  Glass style variant
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Gradient Examples */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Gradient Backgrounds
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(gradientStyles).map(([key, className]) => (
              <motion.div
                key={key}
                className={cn(
                  'p-4 rounded-lg border border-white/10',
                  className,
                  hoverStyles.card
                )}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <h3 className="font-medium text-white capitalize">{key}</h3>
                <p className="text-sm text-gray-300 mt-1">
                  Gradient variant
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Animated Cards Demo */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Animated Metric Cards ({selectedAnimation})
          </h2>
          
          <AnimatePresence mode="wait">
            {showCards && (
              <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
                variants={staggerConfigs.container}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                {demoCards.map((card, index) => (
                  <motion.div
                    key={`${selectedAnimation}-${index}`}
                    className={cn(
                      createCardStyles('glass'),
                      'relative overflow-hidden'
                    )}
                    variants={{
                      initial: { opacity: 0, y: 20 },
                      animate: { opacity: 1, y: 0 },
                      exit: { opacity: 0, y: -20 },
                    }}
                    transition={{
                      delay: index * 0.1,
                      duration: 0.3,
                      ease: 'easeOut',
                    }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Background gradient */}
                    <div className={cn(
                      'absolute inset-0 opacity-20',
                      card.positive ? gradientStyles.success : gradientStyles.danger
                    )} />
                    
                    <div className="relative z-10">
                      <h3 className="text-sm font-medium text-gray-300 mb-2">
                        {card.title}
                      </h3>
                      <p className="text-2xl font-bold text-white mb-1">
                        {card.value}
                      </p>
                      <p className={cn(
                        'text-sm font-medium',
                        card.positive ? 'text-green-400' : 'text-red-400'
                      )}>
                        {card.change}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Hover Effects Demo */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Interactive Elements
          </h2>
          
          <div className="space-y-4">
            <div className="flex flex-wrap gap-4">
              <motion.button
                className={cn(createButtonStyles('primary', 'md'))}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Primary Button
              </motion.button>
              
              <motion.button
                className={cn(createButtonStyles('secondary', 'md'))}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Secondary Button
              </motion.button>
              
              <motion.button
                className={cn(createButtonStyles('danger', 'md'))}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Danger Button
              </motion.button>
            </div>
            
            <div className="flex items-center space-x-4">
              <motion.div
                className="w-12 h-12 bg-primary-500 rounded-full flex items-center justify-center text-white font-bold cursor-pointer"
                whileHover={{ scale: 1.1, rotate: 5 }}
                whileTap={{ scale: 0.9 }}
              >
                <Icon name="Play" size="xl" className="text-white" />
              </motion.div>
              
              <motion.div
                className="w-12 h-12 bg-success-500 rounded-full flex items-center justify-center text-white font-bold cursor-pointer"
                whileHover={{ scale: 1.1, rotate: -5 }}
                whileTap={{ scale: 0.9 }}
              >
                <Icon name="Star" size="xl" className="text-white" />
              </motion.div>
              
              <motion.div
                className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold cursor-pointer"
                whileHover={{ scale: 1.1, rotate: 10 }}
                whileTap={{ scale: 0.9 }}
              >
                <Icon name="Target" size="xl" className="text-white" />
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AnimationDemo;