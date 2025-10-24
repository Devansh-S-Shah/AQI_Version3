export interface Disease {
  id: string;
  name: string;
  symptoms: string[];
  prevention: string[];
  description: string;
}

export const diseases: Disease[] = [
  {
    id: '1',
    name: 'Chronic Obstructive Pulmonary Disease (COPD)',
    description: 'A group of lung diseases that block airflow and make it difficult to breathe. Often caused by long-term exposure to irritating gases or particulate matter.',
    symptoms: [
      'Shortness of breath, especially during physical activities',
      'Wheezing',
      'Chest tightness',
      'Chronic cough with mucus',
      'Frequent respiratory infections',
    ],
    prevention: [
      'Avoid smoking and secondhand smoke',
      'Wear a mask in areas with high air pollution',
      'Keep indoor air clean with air purifiers',
      'Regular exercise to strengthen lungs',
      'Get vaccinated against flu and pneumonia',
    ],
  },
  {
    id: '2',
    name: 'Asthma',
    description: 'A chronic condition in which the airways narrow and swell, producing extra mucus. This can make breathing difficult and trigger coughing, wheezing, and shortness of breath.',
    symptoms: [
      'Difficulty breathing',
      'Chest tightness or pain',
      'Wheezing when exhaling',
      'Coughing or wheezing attacks',
      'Trouble sleeping due to breathing problems',
    ],
    prevention: [
      'Identify and avoid asthma triggers',
      'Monitor your breathing regularly',
      'Use air purifiers to reduce indoor pollutants',
      'Keep humidity levels optimal (30-50%)',
      'Take prescribed medications as directed',
    ],
  },
  {
    id: '3',
    name: 'Lung Cancer',
    description: 'Cancer that begins in the lungs. Long-term exposure to air pollution and carcinogens can increase risk.',
    symptoms: [
      'Persistent cough that worsens over time',
      'Coughing up blood',
      'Chest pain',
      'Unexplained weight loss',
      'Shortness of breath',
    ],
    prevention: [
      'Avoid smoking and exposure to tobacco smoke',
      'Reduce exposure to radon and air pollutants',
      'Test your home for radon',
      'Wear protective equipment if exposed to carcinogens at work',
      'Eat a healthy diet rich in fruits and vegetables',
    ],
  },
  {
    id: '4',
    name: 'Bronchitis',
    description: 'Inflammation of the lining of bronchial tubes, which carry air to and from the lungs. Can be acute or chronic.',
    symptoms: [
      'Cough with mucus',
      'Fatigue',
      'Shortness of breath',
      'Slight fever and chills',
      'Chest discomfort',
    ],
    prevention: [
      'Avoid cigarette smoke and other lung irritants',
      'Wash hands frequently to prevent infections',
      'Get annual flu vaccine',
      'Wear a mask in polluted environments',
      'Maintain good indoor air quality',
    ],
  },
  {
    id: '5',
    name: 'Pneumoconiosis',
    description: 'A group of lung diseases caused by inhaling dust particles that damage the lungs. Common in workers exposed to mineral dusts.',
    symptoms: [
      'Shortness of breath',
      'Chronic cough',
      'Chest tightness',
      'Progressive respiratory failure',
    ],
    prevention: [
      'Use proper respiratory protection in dusty environments',
      'Ensure proper ventilation at workplaces',
      'Regular health screenings if at risk',
      'Avoid areas with high particulate matter',
      'Follow workplace safety regulations',
    ],
  },
];
