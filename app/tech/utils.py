# type: ignore
from zk import ZK, const
from datetime import datetime
from ..models import Employee, AttendanceRecord, ZKMachine, db
import logging
from pytz import timezone


logger = logging.getLogger(__name__)
fh = logging.FileHandler('app.log')
logger.setLevel(logging.DEBUG)

# Create a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(fh)




cairo_tz = timezone('Africa/Cairo')

class ZKConnector:
    """
    Class for handling connections to ZK attendance machines
    """
    
    @staticmethod
    def connect_to_machine(ip, port=4370, timeout=30, retries=3):
        """
        Connect to a ZK machine with retries and increased timeout
        """
        zk = ZK(ip, port=port, timeout=timeout)
        conn = None
        for attempt in range(retries):
            try:
                conn = zk.connect()
                return conn
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed to connect to ZK machine at {ip}:{port} - {e}")
                if conn:
                    conn.disconnect()
                time.sleep(2)  # Wait before retrying
        return None




    # def connect_to_machine(ip, port=4370, timeout=5):
    #     """
    #     Connect to a ZK machine and return the connection object
    #     """
    #     zk = ZK(ip, port=port, timeout=timeout)
    #     conn = None
    #     try:
    #         conn = zk.connect()
    #         return conn
    #     except Exception as e:
    #         logger.error(f"Error connecting to ZK machine at {ip}:{port} - {e}")
    #         if conn:
    #             conn.disconnect()
    #         return None
    
    @staticmethod
    def get_attendance_data(machine_config):
        """
        Get attendance data from a ZK machine
        """
        ip = machine_config['ip']
        port = machine_config['port']
        timeout = machine_config['timeout']
        machine_name = machine_config['name']
        
        conn = ZKConnector.connect_to_machine(ip, port, timeout)
        if not conn:
            return None
        
        try:
            # Get attendance records
            attendance = conn.get_attendance()
            
            # Update machine status in database
            machine = ZKMachine.query.filter_by(ip=ip).first()
            if not machine:
                machine = ZKMachine(
                    name=machine_name,
                    ip=ip,
                    port=port,
                    status='active',
                    last_sync=datetime.now(cairo_tz)
                )
                db.session.add(machine)
            else:
                machine.status = 'active'
                machine.last_sync = datetime.now(cairo_tz)
            
            db.session.commit()
            
            # Process and return attendance records
            return {
                'machine': machine.to_dict(),
                'attendance': [
                    {
                        'user_id': str(att.user_id),
                        'timestamp': att.timestamp.astimezone(cairo_tz),  # Ensure Cairo time zone
                        'status': att.status
                    } for att in attendance
                ]
            }
        except Exception as e:
            logger.error(f"Error getting attendance data from {ip}:{port} - {e}")
            return None
        finally:
            conn.disconnect()




    # def get_attendance_data(machine_config):
    #     """
    #     Get attendance data from a ZK machine
    #     """
    #     ip = machine_config['ip']
    #     port = machine_config['port']
    #     timeout = machine_config['timeout']
    #     machine_name = machine_config['name']
        
    #     conn = ZKConnector.connect_to_machine(ip, port, timeout)
    #     if not conn:
    #         return None
        
    #     try:
    #         # Get attendance records
    #         attendance = conn.get_attendance()
            
    #         # Update machine status in database
    #         machine = ZKMachine.query.filter_by(ip=ip).first()
    #         if not machine:
    #             machine = ZKMachine(
    #                 name=machine_name,
    #                 ip=ip,
    #                 port=port,
    #                 status='active',
    #                 last_sync=datetime.now(cairo_tz)
    #             )
    #             db.session.add(machine)
    #         else:
    #             machine.status = 'active'
    #             machine.last_sync = datetime.now(cairo_tz)
            
    #         db.session.commit()
            
    #         # Process and return attendance records
    #         return {
    #             'machine': machine.to_dict(),
    #             'attendance': [
    #                 {
    #                     'user_id': str(att.user_id),
    #                     'timestamp': att.timestamp.astimezone(cairo_tz),  # Ensure Cairo time zone
    #                     'status': att.status
    #                 } for att in attendance
    #             ]
    #         }
    #     except Exception as e:
    #         logger.error(f"Error getting attendance data from {ip}:{port} - {e}")
    #         return None
    #     finally:
    #         conn.disconnect()



    @staticmethod
    def save_attendance_records(machine_data):
        """
        Save attendance records to the database
        """
        if not machine_data:
            return False
        
        machine = machine_data['machine']
        records = machine_data['attendance']
        
        new_records = []
        for record in records:
            # Convert timestamp to Cairo time zone
            cairo_time = record['timestamp'].astimezone(cairo_tz)

            # Check if record already exists in database
            existing = AttendanceRecord.query.filter_by(
                zk_user_id=record['user_id'],
                timestamp=cairo_time,
                machine_ip=machine['ip']
            ).first()
            
            if not existing:
                # Try to find matching employee
                employee = Employee.query.filter_by(employee_id=record['user_id']).first()
                employee_id = employee.employee_id if employee else None
                
                # Create new attendance record in Cairo Time zone
                new_record = AttendanceRecord(
                    zk_user_id=record['user_id'],
                    employee_id=employee_id,
                    timestamp=cairo_time,
                    machine_name=machine['name'],
                    machine_ip=machine['ip']
                )

                db.session.add(new_record)
                new_records.append(new_record)
        
        if new_records:
            db.session.commit()
            
        return len(new_records)





    # @staticmethod
    # def save_attendance_records(machine_data):

    #     """
    #     Save attendance records to the database
    #     """
    #     if not machine_data:
    #         return False
        
    #     machine = machine_data['machine']
    #     records = machine_data['attendance']
        
    #     new_records = []
    #     for record in records:
    #         # Convert timestamp to Cairo time zone
    #         cairo_time = record['timestamp'].astimezone(cairo_tz)

    #         # Check if record already exists in database
    #         existing = AttendanceRecord.query.filter_by(
    #             zk_user_id=record['user_id'],
    #             timestamp=cairo_time,
    #             machine_ip=machine['ip']
    #         ).first()
            
    #         if not existing:
    #             # Try to find matching employee
    #             employee = Employee.query.filter_by(employee_id=record['user_id']).first()
    #             employee_id = employee.employee_id if employee else None
                
    #             # Create new attendance record in Cairo Time zone
    #             new_record = AttendanceRecord(
    #                 zk_user_id=record['user_id'],
    #                 employee_id=employee_id,
    #                 timestamp=cairo_time,
    #                 machine_name=machine['name'],
    #                 machine_ip=machine['ip']
    #             )

    #             db.session.add(new_record)
    #             new_records.append(new_record)
    
    #     if new_records:
    #         db.session.commit()
            
    #     return len(new_records)





    # def save_attendance_records(machine_data):
    #     """
    #     Save attendance records to the database
    #     """
    #     if not machine_data:
    #         return False
        
    #     machine = machine_data['machine']
    #     records = machine_data['attendance']
        
    #     new_records = []
    #     for record in records:

    #         # Convert timestamp to Cairo time zone
    #         cairo_time = record['timestamp'].astimezone(cairo_tz)


    #         # Check if record already exists in database
    #         existing = AttendanceRecord.query.filter_by(
    #             zk_user_id=record['user_id'],
    #             timestamp=cairo_time,
    #             machine_ip=machine['ip']
    #         ).first()



    #         # Check if record already exists in database
    #         # existing = AttendanceRecord.query.filter_by(
    #         #     zk_user_id=record['user_id'],
    #         #     timestamp=record['timestamp'],
    #         #     machine_ip=machine['ip']
    #         # ).first()
            
    #         if not existing:
    #             # Try to find matching employee
    #             employee = Employee.query.filter_by(employee_id=record['user_id']).first()
    #             employee_id = employee.employee_id if employee else None
                
    #             # Create new attendance record
    #             # new_record = AttendanceRecord(
    #             #     zk_user_id=record['user_id'],
    #             #     employee_id=employee_id,
    #             #     timestamp=record['timestamp'],
    #             #     punch_type=record['punch'],
    #             #     machine_name=machine['name'],
    #             #     machine_ip=machine['ip']
    #             # )

    #             # Create new attendance record in Cairo Time zone
    #             # new_record = AttendanceRecord(
    #             #     zk_user_id=record['user_id'],
    #             #     employee_id=employee_id,
    #             #     timestamp=cairo_time,
    #             #     punch_type=record['punch'],
    #             #     machine_name=machine['name'],
    #             #     machine_ip=machine['ip']
    #             # )


    #             # Create new attendance record in Cairo Time zone
    #             new_record = AttendanceRecord(
    #                 zk_user_id=record['user_id'],
    #                 employee_id=employee_id,
    #                 timestamp=cairo_time,
    #                 machine_name=machine['name'],
    #                 machine_ip=machine['ip']
    #             )


    #             db.session.add(new_record)
    #             new_records.append(new_record)
        
    #     if new_records:
    #         db.session.commit()
            
    #     return len(new_records)

    @staticmethod
    def get_combined_attendance_data():
        """
        Get combined attendance data with employee information
        """
        attendance_records = AttendanceRecord.query.order_by(
            AttendanceRecord.timestamp.desc()
        ).all()
        
        results = []
        for record in attendance_records:
            employee = None
            if record.employee_id:
                employee = Employee.query.filter_by(employee_id=record.employee_id).first()
            
            # results.append({
            #     'record_id': record.id,
            #     'zk_user_id': record.zk_user_id,
            #     'employee_id': record.employee_id,
            #     'employee_name': employee.name if employee else None,
            #     'employee_department': employee.department if employee else None,
            #     'employee_title': employee.title if employee else None,
            #     'timestamp': record.timestamp,
            #     'punch_type': record.punch_type,
            #     'machine_name': record.machine_name
            # })


            results.append({
                'record_id': record.id,
                'zk_user_id': record.zk_user_id,
                'employee_id': record.employee_id,
                'employee_name': employee.name if employee else None,
                'employee_department': employee.department if employee else None,
                'employee_title': employee.title if employee else None,
                'timestamp': record.timestamp,
                'machine_name': record.machine_name
            })
        
        return results
    