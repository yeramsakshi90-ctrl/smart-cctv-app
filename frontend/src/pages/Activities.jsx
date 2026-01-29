import { useState, useEffect } from 'react';
import { activityService } from '../services/activityService';

const Activities = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      const data = await activityService.getAll();
      setActivities(Array.isArray(data) ? data : data.activities || []);
    } catch (err) {
      setError('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Activities</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {activities.length === 0 ? (
            <li className="px-6 py-4 text-center text-gray-500">No activities found</li>
          ) : (
            activities.map((activity) => (
              <li key={activity.id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {activity.activity_type}
                      </span>
                      {activity.confidence_score && (
                        <span className="text-xs text-gray-500">
                          Confidence: {(activity.confidence_score * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-medium text-gray-900">{activity.description}</h3>
                    {activity.camera_name && (
                      <p className="text-sm text-gray-500 mt-1">Camera: {activity.camera_name}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
};

export default Activities;

