import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface RiskIndicatorsProps {
  riskScores: number[];
  features: Record<string, number>;
}

const RiskIndicators: React.FC<RiskIndicatorsProps> = ({ riskScores, features }) => {
  const indicatorNames = [
    'نسبت کل پزشکان به پزشکان منحصر به فرد',
    'نسبت کل بیماران به بیماران منحصر به فرد',
    'درصد تغییر هزینه پزشک',
    'درصد تغییر هزینه بیمار',
    'درصد تفاوت هزینه خدمت',
    'درصد تفاوت هزینه خدمت برای پزشک',
    'درصد تفاوت هزینه تخصص برای پزشک',
    'درصد تفاوت هزینه تخصص مستقیم',
    'درصد تفاوت هزینه خدمت برای بیمار',
    'درصد تفاوت هزینه خدمت کلی',
    'نسبت خدمت'
  ];

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { level: 'بالا', color: 'text-red-600', bgColor: 'bg-red-100' };
    if (score >= 40) return { level: 'متوسط', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    return { level: 'پایین', color: 'text-green-600', bgColor: 'bg-green-100' };
  };

  const getTrendIcon = (score: number) => {
    if (score >= 70) return <TrendingUp className="h-4 w-4 text-red-500" />;
    if (score >= 40) return <Minus className="h-4 w-4 text-yellow-500" />;
    return <TrendingDown className="h-4 w-4 text-green-500" />;
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">تحلیل شاخص‌های ریسک</h3>
        <p className="text-gray-600 mb-6">
          این شاخص‌ها بر اساس الگوریتم‌های یادگیری ماشین محاسبه شده‌اند و نشان‌دهنده احتمال تقلب در نسخه هستند.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {riskScores.map((score, index) => {
          const riskLevel = getRiskLevel(score);
          const featureValue = Object.values(features)[index] || 0;
          
          return (
            <div key={index} className="card">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900 text-sm">
                  شاخص {index + 1}
                </h4>
                {getTrendIcon(score)}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">نام شاخص:</span>
                  <span className="text-xs font-medium text-gray-900 text-right">
                    {indicatorNames[index]}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">مقدار شاخص:</span>
                  <span className="text-xs font-medium text-gray-900">
                    {featureValue.toFixed(2)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">امتیاز ریسک:</span>
                  <span className={`text-sm font-bold ${riskLevel.color}`}>
                    {score.toFixed(1)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-600">سطح ریسک:</span>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${riskLevel.bgColor} ${riskLevel.color}`}>
                    {riskLevel.level}
                  </span>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      score >= 70 ? 'bg-red-500' : score >= 40 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* خلاصه ریسک */}
      <div className="card">
        <h4 className="font-semibold text-gray-900 mb-4">خلاصه تحلیل ریسک</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {riskScores.filter(score => score >= 70).length}
            </div>
            <div className="text-sm text-gray-600">شاخص‌های ریسک بالا</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {riskScores.filter(score => score >= 40 && score < 70).length}
            </div>
            <div className="text-sm text-gray-600">شاخص‌های ریسک متوسط</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {riskScores.filter(score => score < 40).length}
            </div>
            <div className="text-sm text-gray-600">شاخص‌های ریسک پایین</div>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-700">
            <strong>توصیه:</strong> 
            {riskScores.filter(score => score >= 70).length > 3 
              ? ' این نسخه دارای ریسک بالایی است و نیاز به بررسی دقیق‌تر دارد.'
              : riskScores.filter(score => score >= 40).length > 5
              ? ' این نسخه دارای ریسک متوسطی است و توصیه می‌شود بررسی شود.'
              : ' این نسخه دارای ریسک پایینی است و احتمال تقلب کم است.'
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskIndicators;
