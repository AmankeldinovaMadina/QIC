import { useState } from 'react';
import { X, Send } from 'lucide-react';
import { Card } from './ui/card';
import qicoAvatar from 'figma:asset/df749756eb2f3e1f6a511fd7b1a552bd3aabda73.png';

interface AIAssistantButtonProps {
  onOpen?: () => void;
}

export function AIAssistantButton({ onOpen }: AIAssistantButtonProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [message, setMessage] = useState('');

  const handleClick = () => {
    if (!isExpanded) {
      setIsExpanded(true);
      onOpen?.();
    } else {
      setIsExpanded(false);
    }
  };

  const handleSend = () => {
    if (message.trim()) {
      // TODO: Add API endpoint call here
      console.log('Sending message:', message);
      setMessage('');
    }
  };

  return (
    <>
      {/* Floating AI Assistant Button - Fixed Footer - Circular with Avatar */}
      {!isExpanded && (
        <button
          onClick={handleClick}
          className="fixed bottom-6 right-6 w-16 h-16 rounded-full overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 z-[9999] border-2 border-white ring-2 ring-blue-200 hover:ring-blue-400 hover:scale-110 flex items-center justify-center bg-white"
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
          className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-4rem)] h-[500px] max-h-[calc(100vh-8rem)] z-[9999] flex flex-col"
          style={{ 
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            margin: '0'
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
            <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
              <div className="space-y-4 max-w-full">
                {/* Welcome Message from AI */}
                <div className="flex items-start gap-3">
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
                  <div className="flex-1 bg-white rounded-lg p-3 shadow-sm min-w-0">
                    <p className="text-sm text-gray-700 break-words">
                      Hello! I'm Qico AI, your travel assistant. How can I help you with your trip today?
                    </p>
                  </div>
                </div>

                {/* Example user message - can be removed when real chat is implemented */}
                {/* <div className="flex items-start gap-3 justify-end">
                  <div className="flex-1 bg-blue-500 text-white rounded-lg p-3 shadow-sm max-w-[80%] ml-auto">
                    <p className="text-sm">What activities do you recommend for today?</p>
                  </div>
                </div> */}
              </div>
            </div>

            {/* Chat Input Area */}
            <div className="p-4 border-t bg-white">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSend();
                    }
                  }}
                  placeholder="Type your message..."
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
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

