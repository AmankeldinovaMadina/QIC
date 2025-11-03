import { ArrowLeft, Car, Wrench, Droplet, Key, MapPin, Clock } from 'lucide-react';
import { Card } from './ui/card';

interface CarPageProps {
  onBack: () => void;
}

interface CarService {
  id: number;
  name: string;
  description: string;
  icon: any;
  color: string;
}

export function CarPage({ onBack }: CarPageProps) {
  const carServices: CarService[] = [
    {
      id: 1,
      name: 'Car Rental',
      description: 'Rent a car for your needs',
      icon: Key,
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 2,
      name: 'Repair Service',
      description: 'Professional car repairs',
      icon: Wrench,
      color: 'from-orange-500 to-orange-600'
    },
    {
      id: 3,
      name: 'Car Wash',
      description: 'Premium cleaning service',
      icon: Droplet,
      color: 'from-cyan-500 to-cyan-600'
    },
    {
      id: 4,
      name: 'Detailing',
      description: 'Complete car detailing',
      icon: Car,
      color: 'from-purple-500 to-purple-600'
    }
  ];

  const recentServices = [
    {
      id: 1,
      service: 'Car Wash',
      location: 'Downtown Service Center',
      date: 'Oct 25, 2025',
      status: 'Completed'
    },
    {
      id: 2,
      service: 'Oil Change',
      location: 'Main Street Garage',
      date: 'Oct 15, 2025',
      status: 'Completed'
    }
  ];

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white pb-6">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm z-10 px-6 py-4 border-b">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-semibold">Car Services</h1>
            <p className="text-sm text-gray-500">All your vehicle needs</p>
          </div>
        </div>
      </div>

      {/* My Vehicle Card */}
      <div className="px-6 py-4">
        <Card className="p-5 bg-gradient-to-r from-slate-700 to-slate-600 border-0 text-white">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-slate-300 text-sm mb-1">My Vehicle</p>
              <p className="text-xl">Toyota Camry 2023</p>
            </div>
            <Car className="w-8 h-8 text-slate-300" />
          </div>
          <div className="flex gap-4 text-sm">
            <div>
              <p className="text-slate-300">Plate</p>
              <p className="font-medium">ABC-1234</p>
            </div>
            <div>
              <p className="text-slate-300">Last Service</p>
              <p className="font-medium">Oct 25, 2025</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Services Grid */}
      <div className="px-6 py-4">
        <h2 className="font-semibold mb-4">Available Services</h2>
        <div className="grid grid-cols-2 gap-4">
          {carServices.map((service) => {
            const Icon = service.icon;
            return (
              <Card 
                key={service.id}
                className="p-5 border-0 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${service.color} flex items-center justify-center mb-3`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold mb-1">{service.name}</h3>
                <p className="text-sm text-gray-500">{service.description}</p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Recent Services */}
      <div className="px-6 py-4">
        <h2 className="font-semibold mb-4">Service History</h2>
        <div className="space-y-3">
          {recentServices.map((service) => (
            <Card key={service.id} className="p-4 border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold">{service.service}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                    <MapPin className="w-4 h-4" />
                    <span>{service.location}</span>
                  </div>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                  {service.status}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-500 mt-2">
                <Clock className="w-4 h-4" />
                <span>{service.date}</span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-2 gap-3">
          <button className="p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
            Book Service
          </button>
          <button className="p-4 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
            Emergency Help
          </button>
        </div>
      </div>
    </div>
  );
}
