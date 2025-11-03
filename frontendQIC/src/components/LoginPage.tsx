import { useState } from 'react';
import { Plane, User } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card } from './ui/card';

interface LoginPageProps {
  onLogin: (username: string) => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.length >= 3) {
      onLogin(username);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="w-full max-w-[90%] sm:max-w-sm mx-auto">
        <Card className="p-4 sm:p-6 bg-white/95 backdrop-blur-sm shadow-2xl border-0">
          {/* Logo & Title */}
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl flex items-center justify-center mx-auto mb-3 shadow-lg">
              <Plane className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              QICO
            </h1>
            <p className="text-gray-600 mt-1 text-sm">Your Lifestyle Companion</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <User className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="pl-10"
                  required
                  minLength={3}
                />
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 h-11"
              disabled={username.length < 3}
            >
              Continue
            </Button>
          </form>

          <p className="text-xs text-gray-500 text-center mt-4">
            By continuing, you agree to our Terms of Service and Privacy Policy
          </p>
        </Card>
      </div>
    </div>
  );
}