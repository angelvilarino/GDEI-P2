"""
Employees: web views (placeholder) + REST API endpoints.
"""
from flask import Blueprint, jsonify, request, abort, current_app
from app.services import entity_service

employees_bp = Blueprint('employees', __name__)


# ---------------------------------------------------------------------------
# Views (text placeholder — HTML templates to be added in Issue #4)
# ---------------------------------------------------------------------------

@employees_bp.route('/employees')
def employees_list():
    return "EMPLOYEES LIST — template pending (Issue #4)", 200


@employees_bp.route('/employees/<employee_id>')
def employee_detail(employee_id):
    return f"EMPLOYEE DETAIL [{employee_id}] — template pending (Issue #4)", 200


# ---------------------------------------------------------------------------
# API — list + create
# ---------------------------------------------------------------------------

@employees_bp.route('/api/employees', methods=['GET'])
def api_employees_list():
    return jsonify(entity_service.get_employees())


@employees_bp.route('/api/employees', methods=['POST'])
def api_employees_create():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        employee = entity_service.create_employee(data)
        return jsonify(employee), 201
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"create_employee: {e}")
        abort(500)


# ---------------------------------------------------------------------------
# API — detail + update + delete
# ---------------------------------------------------------------------------

@employees_bp.route('/api/employees/<employee_id>', methods=['GET'])
def api_employee_detail(employee_id):
    employee = entity_service.get_employee(employee_id)
    if employee is None:
        abort(404, description=f"Employee '{employee_id}' not found")
    return jsonify(employee)


@employees_bp.route('/api/employees/<employee_id>', methods=['PUT'])
def api_employee_update(employee_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        employee = entity_service.update_employee(employee_id, data)
        if employee is None:
            abort(404, description=f"Employee '{employee_id}' not found")
        return jsonify(employee)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"update_employee: {e}")
        abort(500)


@employees_bp.route('/api/employees/<employee_id>', methods=['DELETE'])
def api_employee_delete(employee_id):
    if not entity_service.delete_employee(employee_id):
        abort(404, description=f"Employee '{employee_id}' not found")
    return jsonify({"message": f"Employee '{employee_id}' deleted"})
