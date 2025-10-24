import React from 'react';

// --- Helper Functions to Map Urgency (Uppercase) to Display Text and CSS Class ---

const getPriorityStatus = (urgency) => {
    // We check the uppercase input directly first for performance and clarity
    if (urgency === 'HIGH') return 'HIGH PRIORITY';
    if (urgency === 'MEDIUM') return 'MEDIUM PRIORITY';
    if (urgency === 'LOW') return 'LOW PRIORITY';
    if (urgency === 'MANUAL') return 'MANUAL ENTRY'; // Handles the manual fallback

    // Default for UNSCORED or unexpected values
    return 'MEDIUM PRIORITY';
}

const getPriorityClass = (urgency) => {
    // We convert the input to lowercase only to match the desired CSS class names (high, medium, low)
    const urgencyLower = urgency ? urgency.toLowerCase() : 'medium'; 
    
    if (urgencyLower === 'high') {
        return 'high'; // CSS class: .high
    }
    if (urgencyLower === 'medium' || urgencyLower === 'manual') {
        return 'medium'; // CSS class: .medium (neutral color)
    }
    if (urgencyLower === 'low') {
        return 'low'; // CSS class: .low
    }
    
    return 'medium'; // Default class
}

// ------------------------------------------------------------------

const RequestTable = ({ requests }) => {

    return (
        <div className="table-container">
            <table className="request-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Prediction</th> 
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {requests && requests.length > 0 ? (
                        requests.map(request => (
                            <tr key={request.id}>
                                <td>{request.title || request.description}</td> 
                                <td>
                                    {/* CRITICAL FIX APPLIED: Uses request.urgency for both helper functions */}
                                    <span 
                                        className={`priority-tag ${getPriorityClass(request.urgency)}`}
                                        // Optional: Display confidence as a title tooltip
                                        title={`Confidence: ${request.confidence ? (request.confidence * 100).toFixed(2) + '%' : 'N/A'}`}
                                    >
                                        {getPriorityStatus(request.urgency)}
                                    </span>
                                </td>
                                <td>{new Date(request.date || parseInt(request.id)).toLocaleDateString()}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="3" style={{textAlign: 'center', padding: '20px'}}>
                                No requests found. Create a new one above!
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default RequestTable;