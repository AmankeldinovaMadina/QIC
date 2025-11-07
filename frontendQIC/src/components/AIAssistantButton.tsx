import { useState, useRef, useEffect } from 'react';
import { X, Send } from 'lucide-react';
import { Card } from './ui/card';
import qicoAvatar from 'figma:asset/df749756eb2f3e1f6a511fd7b1a552bd3aabda73.png';

interface AIAssistantButtonProps {
  onOpen?: () => void;
}

interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const MOCK_RESPONSES = [
  "For Dubai, I recommend lightweight, breathable fabrics like cotton and linen. Pack loose-fitting, modest clothing that covers shoulders and knees for cultural respect. Bring a light jacket or cardigan for air-conditioned spaces. Comfortable walking shoes are essential, and don't forget sunglasses and a hat for sun protection. Swimwear is fine for beaches and pools, but cover up when leaving those areas.",
  "You can buy travel insurance through several options:\n\n1. **Online providers**: Compare plans on sites like World Nomads, Allianz, or SafetyWing\n2. **Travel booking sites**: Many airlines and booking platforms offer insurance during checkout\n3. **Insurance brokers**: Contact a local insurance agent for personalized options\n4. **Credit card benefits**: Check if your credit card includes travel insurance\n\nI recommend getting coverage for medical emergencies, trip cancellation, and lost luggage. Make sure to read the policy details carefully!",
  "Having $150 for personal expenses during your trip can work, but it depends on your destination and travel style:\n\n✅ **It's normal if**: You're in a budget-friendly destination, have most expenses pre-paid (hotels, flights), or prefer free/low-cost activities\n\n⚠️ **Consider more if**: You're in expensive cities, want to shop, dine at nice restaurants, or enjoy paid attractions\n\n💡 **Tips**: Set a daily budget ($20-30/day), prioritize experiences over souvenirs, and track your spending. Many travelers successfully travel on tight budgets!"
];

export function AIAssistantButton({ onOpen }: AIAssistantButtonProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [message, setMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      text: "Hello! I'm Qico AI, your travel assistant. How can I help you with your trip today?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [responseIndex, setResponseIndex] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  // Simple input handler - no auto-complete, just normal typing
  const handleInputChange = (e: { target: { value: string } }) => {
    setMessage(e.target.value);
  };

  const handleClick = () => {
    if (!isExpanded) {
      setIsExpanded(true);
      onOpen?.();
    } else {
      setIsExpanded(false);
    }
  };

  const getAIResponse = (): string => {
    // Return mock responses in order, cycling through them
    const response = MOCK_RESPONSES[responseIndex];
    setResponseIndex((prev) => (prev + 1) % MOCK_RESPONSES.length);
    return response;
  };

  const handleSend = () => {
    if (message.trim()) {
      const userMessage = message.trim();
      
      // Add user message
      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        text: userMessage,
        isUser: true,
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, userMsg]);
      setMessage('');
      
      // Simulate AI thinking delay, then add AI response
      setTimeout(() => {
        const aiResponse = getAIResponse();
        const aiMsg: ChatMessage = {
          id: `ai-${Date.now()}`,
          text: aiResponse,
          isUser: false,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiMsg]);
      }, 500);
    }
  };

  return (
    <>
      {/* Floating AI Assistant Button - Fixed Footer - Circular with Avatar */}
      {!isExpanded && (
        <button
          onClick={handleClick}
          className="fixed bottom-6 -right-6 w-16 h-16 rounded-full overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 z-[9999] border-2 border-white ring-2 ring-blue-200 hover:ring-blue-400 hover:scale-110 flex items-center justify-center bg-white"
          aria-label="Chat with AI"
          style={{ 
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <img 
            src={qicoAvatar} 
            alt="Qico AI Assistant" 
            className="w-full h-full object-cover object-center"
            style={{ 
              objectFit: 'cover',
              objectPosition: 'center'
            }}
          />
        </button>
      )}

      {/* Expanded Chat Panel */}
      {isExpanded && (
        <div 
          className="fixed bottom-6 -right-6 w-96 max-w-[calc(100vw-4rem)] z-[9999] flex flex-col"
          style={{ 
            position: 'fixed',
            bottom: '24px',
            right: '0px',
            margin: '0',
            maxHeight: '50vh',
            height: '50vh'
          }}
        >
          <Card className="flex flex-col h-full shadow-2xl border-2 border-blue-200 rounded-lg overflow-hidden">
            {/* Chat Header */}
            <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
              <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 border-2 border-white/30 flex items-center justify-center bg-white">
                <img 
                  src={qicoAvatar} 
                  alt="Qico AI" 
                  className="w-full h-full object-cover object-center"
                  style={{ 
                    objectFit: 'cover',
                    objectPosition: 'center'
                  }}
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold">Chat with AI</p>
                <p className="text-xs text-blue-100">Qico AI Assistant</p>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors flex-shrink-0"
                aria-label="Close Chat"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>

            {/* Chat Messages Area */}
            <div 
              ref={messagesContainerRef}
              className="flex-1 p-4 overflow-y-auto bg-gray-50"
              style={{ 
                minHeight: 0,
                maxHeight: '100%',
                overflowY: 'auto'
              }}
            >
              <div className="space-y-4 max-w-full">
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex items-start gap-3 ${msg.isUser ? 'justify-end' : ''}`}
                  >
                    {!msg.isUser && (
                      <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 flex items-center justify-center bg-white">
                        <img 
                          src={qicoAvatar} 
                          alt="AI" 
                          className="w-full h-full object-cover object-center"
                          style={{ 
                            objectFit: 'cover',
                            objectPosition: 'center'
                          }}
                        />
                      </div>
                    )}
                    <div
                      className={`flex-1 rounded-lg p-3 shadow-sm min-w-0 ${
                        msg.isUser
                          ? 'bg-blue-500 text-black max-w-[80%] ml-auto'
                          : 'bg-white text-gray-700'
                      }`}
                    >
                      <p className={`text-sm break-words whitespace-pre-line ${msg.isUser ? 'text-black' : 'text-gray-700'}`}>
                        {msg.text}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Chat Input Area */}
            <div className="p-4 border-t bg-white">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={handleInputChange}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleSend();
                    }
                    // Allow backspace to work normally
                    if (e.key === 'Backspace') {
                      // Let backspace work normally, don't interfere
                    }
                  }}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm text-gray-900"
                  style={{ color: '#000000' }}
                />
                <button
                  onClick={handleSend}
                  disabled={!message.trim()}
                  className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md flex-shrink-0"
                  aria-label="Send message"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}

