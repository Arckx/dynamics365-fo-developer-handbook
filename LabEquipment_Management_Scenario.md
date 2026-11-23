# Laboratory Equipment Management System (LEMS)
## A Scenario Mapping VSI Asset Management Patterns to Lab Equipment Domain

---

## Executive Summary

This document presents a **complete scenario translation** of the VSI Asset Management codebase patterns into a **Laboratory Equipment Management System (LEMS)**. Every architectural pattern, class structure, workflow, and data model from VSI is mapped to an equivalent lab equipment concept, preserving the exact same logic while changing only the business domain terminology.

**Purpose**: Demonstrate how the VSI patterns are domain-agnostic and reusable across asset-intensive industries.

---

## Domain Mapping Table

| VSI Concept | LEMS Equivalent | Rationale |
|-------------|-----------------|-----------|
| **Asset** | **Equipment** | Core tracked item |
| **AssetType** | **EquipmentModel** | Classification with category |
| **AssetTypeCategory** | **EquipmentClass** | Hardware/Mobile/QA/Network/License → Analytical/Imaging/Compute/Consumable/Calibrated |
| **AssetTag** | **EquipmentTag** | Physical label/barcode |
| **SerialNumber** | **SerialNumber** | Manufacturer serial |
| **VSIAssetLicense** | **EquipmentCalibration** | Seat count → Calibration validity period; Renewal date → Next calibration due |
| **VSIAssetAssignmentHistory** | **EquipmentCheckoutLog** | Assignment → Checkout/Check-in |
| **VSIAssetMaintenance** | **EquipmentServiceRecord** | Fault → Service/Repair/Calibration |
| **VSIAssetRequest** | **EquipmentReservation** | Request → Reservation for experiment |
| **VSIAssetRetirement** | **EquipmentDecommission** | Retirement → Decommission/Disposal |
| **VSIAssetStatusHistory** | **EquipmentStatusLog** | Complete audit trail |
| **VSIAssetStatus** | **EquipmentStatus** | InStock/Assigned/UnderRepair/Retired → Available/CheckedOut/InService/Decommissioned |
| **VSIWorker** | **LabPersonnel** | Researchers, Technicians, Lab Managers |
| **VSIFunctionalLocation** | **LabLocation** | Building → Lab → Bench → Storage |
| **VSIVendor** | **EquipmentVendor** | Manufacturers, calibration services |
| **VSIApprovalStatus** | **ReservationApprovalStatus** | Draft/Pending/Approved/Rejected |
| **VSIRequestStatus** | **ReservationStatus** | Draft/PendingApproval/Approved/Rejected/Fulfilled/Cancelled |
| **VSIMaintenanceStatus** | **ServiceStatus** | Reported/InProgress/Resolved/Unrepairable → Reported/InService/Completed/Unserviceable |
| **VSIAssignmentAction** | **CheckoutAction** | Assign/Return/Reassign → Checkout/Checkin/Transfer |
| **VSIStatusChangeReason** | **StatusChangeReason** | Registration/Assignment/Return/RepairStart/RepairEnd/Retirement → Registration/Checkout/Checkin/ServiceStart/ServiceEnd/Decommission |

---

## Core Data Model (Tables)

### 1. Equipment (≡ VSIAsset)
```xpp
class LEMEquipment extends common
{
    // Key fields
    EquipmentId         // ≡ AssetId (NumberSeq: LEMEquipmentId)
    EquipmentModelId    // ≡ AssetTypeId (FK → LEMEquipmentModel)
    LabLocationId       // ≡ LocationId (FK → LEMLabLocation)
    VendorId            // ≡ VendorId (FK → LEMEquipmentVendor)
    EquipmentTag        // ≡ AssetTag (Physical label, mandatory)
    SerialNumber        // ≡ SerialNumber
    Manufacturer        // ≡ Manufacturer
    Model               // ≡ Model
    PurchaseDate        // ≡ PurchaseDate
    WarrantyExpiryDate  // ≡ WarrantyExpiryDate
    Cost                // ≡ Cost
    Status              // ≡ Status (EquipmentStatus enum)
    LastCalibrationAlertDate  // ≡ LastWarrantyAlertDate
    
    // Display methods
    display EquipmentClass category()        // ≡ category()
    display Name vendorName()                // ≡ vendorName()
    display Name custodianName()             // ≡ custodianName() (current holder)
    display Name reportHolder()              // ≡ reportHolder() (for reports)
    display str tagBarcode()                 // ≡ tagBarcode() (Code 128)
    display str tagBarcodeFont()             // ≡ tagBarcodeFont()
    
    // Business logic
    boolean isCalibrated()                   // ≡ isLicense() - equipment requiring calibration
    boolean isSerialTracked()                // ≡ isSerialTracked()
    boolean canCheckout()                    // ≡ canAssign()
    boolean canCheckin()                     // ≡ canReturn()
    boolean canTransfer()                    // ≡ canReassign()
    boolean canRequestService()              // ≡ canReportFault()
    boolean isDecommissionable()             // ≡ isRetirable()
    boolean canDecommission()                // ≡ canRetire()
}
```

### 2. EquipmentModel (≡ VSIAssetType)
```xpp
class LEMEquipmentModel extends common
{
    EquipmentModelId    // PK
    Name                // e.g., "GC-MS 7890B", "Confocal Microscope"
    Description
    EquipmentClass      // Enum: Analytical, Imaging, Compute, Consumable, Calibrated
    IsSerialTracked     // NoYes
    Active              // NoYes
}
```

### 3. EquipmentCalibration (≡ VSIAssetLicense)
```xpp
class LEMEquipmentCalibration extends common
{
    EquipmentId         // FK (1:1 with Equipment)
    CalibrationIntervalDays  // ≡ SeatCount (how often calibration needed)
    NextCalibrationDate       // ≡ RenewalDate
    CalibrationCost           // ≡ AnnualCost
    LastCalibrationAlertDate  // ≡ LastAlertSentDate
    
    // Display method
    display int calibrationsDue()  // ≡ seatsInUse() - count of overdue calibrations
}
```

### 4. EquipmentCheckoutLog (≡ VSIAssetAssignmentHistory)
```xpp
class LEMEquipmentCheckoutLog extends common
{
    CheckoutId          // PK (NumberSeq: LMCheckoutId)
    EquipmentId         // FK
    PersonnelId         // FK → LabPersonnel
    ReservationId       // FK → EquipmentReservation (nullable)
    LabLocationId       // FK (location at checkout time)
    CheckedOutDateTime  // ≡ AssignedDateTime
    CheckedInDateTime   // ≡ ReturnedDateTime (null = currently checked out)
    
    // Static methods
    static int openCount(EquipmentId _equipmentId)      // ≡ openCount()
    static LEMEquipmentCheckoutLog findOpen(EquipmentId _equipmentId)  // ≡ findOpen()
    static boolean isOpenHolder(EquipmentId, PersonnelId)  // ≡ isOpenHolder()
    static EquipmentCheckoutId newId()                  // ≡ newId()
    
    // Display methods
    display EquipmentTag equipmentTag()  // ≡ assetTag()
    display Name personnelName()         // ≡ workerName()
}
```

### 5. EquipmentServiceRecord (≡ VSIAssetMaintenance)
```xpp
class LEMEquipmentServiceRecord extends common
{
    ServiceId           // PK (NumberSeq: LMServiceId)
    EquipmentId         // FK
    RequestedByPersonnelId  // FK (who reported)
    TechnicianPersonnelId   // FK (assigned tech)
    IssueDescription    // ≡ IssueDescription
    ServiceStatus       // Enum: Reported, InService, Completed, Unserviceable
    LoggedDateTime      // ≡ LoggedDateTime
    CompletedDateTime   // ≡ ResolvedDateTime
    ResolutionNotes     // ≡ ResolutionNotes
    ServiceCost         // ≡ RepairCost
    
    // Business logic
    static boolean hasOpenService(EquipmentId _equipmentId)  // ≡ hasOpenTicket()
    static LEMEquipmentServiceRecord find(ServiceId, forUpdate)
    boolean canStartService()    // ≡ canStartRepair()
    boolean canEditTechnician()  // ≡ canEditTechnician()
    boolean canComplete()        // ≡ canFinish()
    boolean canDecommissionEquipment()  // ≡ canRetireAsset()
    static void startService(ServiceId)  // ≡ startRepair()
    
    // Workflow integration
    boolean canSubmitToWorkflow()
    static void completeByRecId(RecId)      // ≡ resolveByRecId()
    static void markUnserviceableByRecId(RecId)  // ≡ markUnrepairableByRecId()
}
```

### 6. EquipmentReservation (≡ VSIAssetRequest)
```xpp
class LEMEquipmentReservation extends common
{
    ReservationId       // PK (NumberSeq: LMReservationId)
    EquipmentModelId    // FK (type of equipment needed)
    RequestorPersonnelId  // FK
    ApprovedByPersonnelId // FK (nullable)
    Justification       // Experiment/project description
    EstimatedCost
    ReservationStatus   // Enum: Draft, PendingApproval, Approved, Rejected, Fulfilled, Cancelled
    ApprovalDate
    
    // Business logic
    boolean isEditable()          // ≡ isEditable() (only Draft)
    boolean canSubmitToWorkflow() // ≡ canSubmitToWorkflow()
    boolean canFulfil()           // ≡ canFulfil()
    static void markFulfilled(ReservationId)  // ≡ markFulfilled()
    static void changeStatusByRecId(RecId, status, approver)
    boolean validateForSubmission()
    
    // Display methods
    display Name requestorName()
    display Name approverName()
}
```

### 7. EquipmentDecommission (≡ VSIAssetRetirement)
```xpp
class LEMEquipmentDecommission extends common
{
    DecommissionId      // PK (NumberSeq: LMDecommissionId)
    EquipmentId         // FK
    ServiceId           // FK (optional, linked unserviceable service record)
    RequestedByPersonnelId
    DecommissionedByPersonnelId  // FK (nullable)
    DecommissionReason  // Enum: EndOfLife, Damaged, Obsolete, GrantEnded
    DisposalMethod      // Enum: Recycled, Sold, Donated, Destroyed, NotApplicable
    DataWipeConfirmed   // NoYes (for equipment with storage)
    ApprovalStatus      // Enum: Draft, PendingApproval, Approved, Rejected
    DecommissionedDateTime
    
    // Business logic
    LEMEquipment equipment()
    LEMEquipmentServiceRecord service()
    boolean isTicketValid()  // ≡ isTicketValid()
    boolean validateWrite()  // Validates: no duplicate, asset state, disposal method, ticket
    boolean validateDelete() // Only Draft
    boolean canSubmitToWorkflow()
    static boolean existsForEquipment(EquipmentId)
    boolean canReopen()       // ≡ canReopen() (Rejected + equipment still decommissionable)
    static void reopenByRecId(RecId)
    static void approveByRecId(RecId, approverPersonnelId)
    static void changeApprovalStatusByRecId(RecId, status)
    boolean isApprovalTransitionAllowed(from, to)
    
    // Display methods
    display Name requesterName()
    display Name decommissionedByName()
    display EquipmentTag equipmentTag()
    display Name equipmentModelName()
    display EquipmentStatus equipmentStatus()
    display Name equipmentVendorName()
    display TransDateTime serviceLoggedDateTime()
    display Notes serviceResolutionNotes()
}
```

### 8. EquipmentStatusLog (≡ VSIAssetStatusHistory)
```xpp
class LEMEquipmentStatusLog extends common
{
    LogId               // PK (NumberSeq: LMStatusHistoryId)
    EquipmentId         // FK
    CheckoutId          // FK (nullable)
    ServiceId           // FK (nullable)
    DecommissionId      // FK (nullable)
    ChangedByPersonnelId
    OldStatus           // EquipmentStatus
    NewStatus           // EquipmentStatus
    Reason              // StatusChangeReason enum
    ChangeDateTime      // UTC
    
    // Static logging method
    static void log(EquipmentId, OldStatus, NewStatus, Reason, ChangedByPersonnelId, 
                    CheckoutId, ServiceId, DecommissionId)
    
    // Validation: Registration needs no refs; Checkout/Checkin need CheckoutId; 
    // ServiceStart/End need ServiceId; Decommission needs DecommissionId
    // Non-Registration must change status
    boolean validateWrite()
    
    display Name changedByName()
}
```

### 9. LEMEquipmentParameters (≡ VSIAssetParameters)
```xpp
class LEMEquipmentParameters extends common
{
    Key                 // Singleton (0)
    
    // Number sequence references (8 total)
    static NumberSequenceReference numRefEquipmentId()
    static NumberSequenceReference numRefReservationId()
    static NumberSequenceReference numRefServiceId()
    static NumberSequenceReference numRefDecommissionId()
    static NumberSequenceReference numRefCheckoutId()
    static NumberSequenceReference numRefStatusHistoryId()
    static NumberSequenceReference numRefPersonnelId()    // Global scope
    static NumberSequenceReference numRefVendorId()       // Global scope
}
```

### 10. LabPersonnel (≡ VSIWorker)
```xpp
class LEMLabPersonnel extends common
{
    PersonnelId         // PK (NumberSeq: LMPersonnelId, global)
    PersonnelNumber     // HR employee ID (unique, locked after create)
    PlatformUserId      // Azure AD UPN (unique, locked after create)
    Name
    Department
    JobTitle            // Researcher, Technician, LabManager, PI
    Email
    IsTechnician        // NoYes (can be assigned service tasks)
    IsLabManager        // NoYes (receives alerts, approves)
    EmploymentStatus    // Active, Inactive
    
    // Static methods
    static LEMLabPersonnel findByPlatformUserId(PlatformUserId)  // ≡ findByPlatformUserId()
    static void lookupActive(FormControl, excludePersonnelId)    // ≡ lookupActive()
    static LEMLabPersonnel find(PersonnelId, forUpdate)
    static boolean isActive(PersonnelId)
    static void lookupTechnician(FormControl)    // ≡ lookupTechnician()
    static boolean isActiveTechnician(PersonnelId)
    
    // Validation: unique PersonnelNumber, unique PlatformUserId
}
```

### 11. LEMLabLocation (≡ VSIFunctionalLocation)
```xpp
class LEMLabLocation extends common
{
    LabLocationId       // PK
    ParentLabLocationId // Self-ref (hierarchy)
    Name
    LocationType        // Enum: Building, Lab, Bench, Storage, Remote
    Active              // NoYes
    
    // Hierarchy methods
    Set descendantIds()  // ≡ descendantIds() - all child locations
    boolean validateWrite()  // No circular refs (parent ≠ self, parent not in descendants)
    boolean validateDelete() // No children, no equipment assigned
    static void lookupActive(FormControl)
    
    // Tree form support
    Map treeIndexByRecId
    void buildTree(RecId selectRecId)
    void addNodes(parentIdx, parentLocationId, childrenMap)
    void selectNode(RecId)
    void createLocation(parentLocationId)
}
```

### 12. LEMEquipmentVendor (≡ VSIVendor)
```xpp
class LEMEquipmentVendor extends common
{
    VendorId            // PK (NumberSeq: LMVendorId, global)
    VendorAccountNum    // ERP vendor account (unique)
    Name
    VendorStatus        // Active, Blocked
    
    static void lookupActive(FormControl)
    static LEMEquipmentVendor find(VendorId, forUpdate)
    boolean validateWrite()  // Unique VendorAccountNum
}
```

---

## Enums (Direct Mapping)

```xpp
// ≡ VSIAssetStatus
enum EquipmentStatus
{
    Available,      // ≡ InStock
    CheckedOut,     // ≡ Assigned
    InService,      // ≡ UnderRepair
    Decommissioned  // ≡ Retired
}

// ≡ VSIAssetStatusFilter
enum EquipmentStatusFilter
{
    All,
    Available,
    CheckedOut,
    InService,
    Decommissioned
}

// ≡ VSIAssetTypeCategory
enum EquipmentClass
{
    Analytical,     // ≡ Hardware (GC-MS, HPLC, Spectrometers)
    Imaging,        // ≡ Mobile (Microscopes, Imaging systems)
    Compute,        // ≡ QATest (HPC, Analysis workstations)
    Consumable,     // ≡ Network (Columns, reagents, tips)
    Calibrated      // ≡ License (Equipment requiring periodic calibration)
}

// ≡ VSIAssignmentAction
enum CheckoutAction
{
    Checkout,       // ≡ Assign
    Checkin,        // ≡ Return
    Transfer        // ≡ Reassign
}

// ≡ VSIRequestStatus
enum ReservationStatus
{
    Draft,
    PendingApproval,
    Approved,
    Rejected,
    Fulfilled,
    Cancelled
}

// ≡ VSIApprovalStatus
enum ReservationApprovalStatus
{
    Draft,
    PendingApproval,
    Approved,
    Rejected
}

// ≡ VSIMaintenanceStatus
enum ServiceStatus
{
    Reported,
    InService,
    Completed,
    Unserviceable
}

// ≡ VSIMaintenanceAction
enum ServiceAction
{
    StartService,   // ≡ StartRepair
    Complete,       // ≡ Resolve
    MarkUnserviceable  // ≡ Unrepairable
}

// ≡ VSIDisposalMethod
enum DisposalMethod
{
    Recycled,
    Sold,
    Donated,
    Destroyed,
    NotApplicable
}

// ≡ VSIRetirementReason
enum DecommissionReason
{
    EndOfLife,
    Damaged,
    Obsolete,
    GrantEnded
}

// ≡ VSIStatusChangeReason
enum StatusChangeReason
{
    Registration,
    Checkout,       // ≡ Assignment
    Checkin,        // ≡ Return
    ServiceStart,   // ≡ RepairStart
    ServiceEnd,     // ≡ RepairEnd
    Decommission,   // ≡ Retirement
    Migration,
    Correction
}

// ≡ VSIEmploymentStatus
enum EmploymentStatus
{
    Active,
    Inactive
}

// ≡ VSILocationType
enum LabLocationType
{
    Building,
    Lab,
    Bench,
    Storage,
    Remote
}

// ≡ VSIExpiryType
enum CalibrationType
{
    Warranty,       // Manufacturer warranty
    Calibration     // Periodic calibration
}

// ≡ VSIServiceDirection
enum ServiceDirection
{
    Inbound,
    Outbound
}

// ≡ VSIVendorStatus
enum VendorStatus
{
    Active,
    Blocked
}
```

---

## Core Business Logic Classes

### 1. EquipmentStatusHelper (≡ VSIAssetStatusHelper)
```xpp
class LEMEquipmentStatusHelper
{
    // Valid transitions (same logic as VSI)
    static boolean isTransitionAllowed(EquipmentStatus from, EquipmentStatus to)
    {
        switch (from)
        {
            case EquipmentStatus::Available:
                return to == EquipmentStatus::CheckedOut
                    || to == EquipmentStatus::InService
                    || to == EquipmentStatus::Decommissioned;
            case EquipmentStatus::CheckedOut:
                return to == EquipmentStatus::Available
                    || to == EquipmentStatus::InService;
            case EquipmentStatus::InService:
                return to == EquipmentStatus::CheckedOut
                    || to == EquipmentStatus::Available
                    || to == EquipmentStatus::Decommissioned;
            default:
                return false;
        }
    }
    
    static void changeStatus(
        EquipmentId _equipmentId,
        EquipmentStatus _newStatus,
        StatusChangeReason _reason,
        PersonnelId _changedByPersonnelId,
        CheckoutId _checkoutId = '',
        ServiceId _serviceId = '',
        DecommissionId _decommissionId = '')
    {
        // Exact same pattern as VSIAssetStatusHelper::changeStatus()
        // Uses LEMEquipmentStatusChangeContext guard
        // Logs to LEMEquipmentStatusLog::log()
    }
}
```

### 2. EquipmentStatusChangeContext (≡ VSIAssetStatusChangeContext)
```xpp
class LEMEquipmentStatusChangeContext implements IDisposable
{
    private static LEMEquipmentStatusChangeContext instance;
    
    public void new()  { if (instance) throw error("Nested"); instance = this; }
    public void dispose() { instance = null; }
    public static boolean isActive() { return instance != null; }
}
```

### 3. EquipmentCheckoutHelper (≡ VSIAssetAssignmentHelper)
```xpp
class LEMEquipmentCheckoutHelper
{
    // Checkout (≡ Assign)
    static CheckoutId checkout(
        EquipmentId _equipmentId,
        PersonnelId _personnelId,
        PersonnelId _actorPersonnelId,
        ReservationId _reservationId = '')
    {
        // Validates: equipment exists, not decommissioned/in-service
        // For Calibrated equipment: checks calibration validity (≡ seat count)
        // For non-calibrated: must be Available
        // Creates LEMEquipmentCheckoutLog
        // Changes status to CheckedOut via EquipmentStatusHelper
        // Marks reservation Fulfilled if provided
    }
    
    // Checkin (≡ Return)
    static void checkin(
        EquipmentId _equipmentId,
        PersonnelId _personnelId,
        PersonnelId _actorPersonnelId)
    {
        // Finds open checkout, sets CheckedInDateTime
        // If no more open checkouts → status to Available
    }
    
    // Transfer (≡ Reassign)
    static void transfer(
        EquipmentId _equipmentId,
        PersonnelId _fromPersonnelId,
        PersonnelId _toPersonnelId)
    {
        // Closes from-checkout, creates to-checkout
        // Validates: to-personnel active, not same, not already holding (for calibrated)
    }
}
```

### 4. EquipmentCheckoutAction (≡ VSIAssetAssignmentAction)
```xpp
class LEMEquipmentCheckoutAction
{
    // Form action entry point (menu items: LMEquipmentCheckout, LMEquipmentCheckin, LMEquipmentTransfer)
    static void main(Args _args)
    {
        // Gets equipment from caller, action from parmEnum()
        // Dialog with from/to/performed-by personnel fields
        // Lookups: active personnel, technicians, current holders
        // Validates via EquipmentCheckoutHelper
    }
}
```

### 5. EquipmentCheckoutContext (≡ VSIAssetStatusChangeContext for assignments)
```xpp
// Handled by EquipmentStatusChangeContext during status changes
// Assignment/Return create status history with Reason=Checkout/Checkin
```

---

## Workflow Classes (Exact Structural Mapping)

### EquipmentReservation Workflow
```xpp
// ≡ VSIAssetRequestWorkflow
class LEMEquipmentReservationWorkflowDocument extends WorkflowDocument
{
    queryName getQueryName() { return queryStr(LEMEquipmentReservationWorkflowQuery); }
}

// ≡ VSIAssetRequestWorkflowEventHandler (7 interfaces)
class LEMEquipmentReservationWorkflowEventHandler implements
    WorkflowCanceledEventHandler,
    WorkflowCompletedEventHandler,
    WorkflowStartedEventHandler
{
    void started(WorkflowEventArgs args)
    {
        LEMEquipmentReservation::changeStatusByRecId(
            args.parmWorkflowContext().parmRecId(),
            ReservationStatus::PendingApproval);
    }
    void canceled(WorkflowEventArgs args)
    {
        LEMEquipmentReservation::changeStatusByRecId(
            args.parmWorkflowContext().parmRecId(),
            ReservationStatus::Draft);
    }
    void completed(WorkflowEventArgs args) { }
}

// ≡ VSIAssetRequestApprovalEventHandler (6 interfaces)
class LEMEquipmentReservationApprovalEventHandler implements
    WorkflowElementCanceledEventHandler,
    WorkflowElemChangeRequestedEventHandler,
    WorkflowElementCompletedEventHandler,
    WorkflowElementReturnedEventHandler,
    WorkflowElementStartedEventHandler,
    WorkflowWorkItemsCreatedEventHandler
{
    void started(WorkflowElementEventArgs args)
    {
        LEMEquipmentReservation::changeStatusByRecId(
            args.parmWorkflowContext().parmRecId(),
            ReservationStatus::PendingApproval);
    }
    void completed(WorkflowElementEventArgs args)
    {
        PersonnelId approver = LMEWorkflowActorHelper::approverPersonnelIdOrBlank(
            args.parmWorkflowContext().parmTableId(),
            args.parmWorkflowContext().parmRecId());
        LEMEquipmentReservation::changeStatusByRecId(
            args.parmWorkflowContext().parmRecId(),
            ReservationStatus::Approved,
            approver);
    }
    void changeRequested(...) { changeStatusByRecId(recId, ReservationStatus::Draft); }
    void returned(...) { changeStatusByRecId(recId, ReservationStatus::Rejected); }
    void canceled(...) { changeStatusByRecId(recId, ReservationStatus::Draft); }
    void created(...) { }
}

// ≡ VSIAssetRequestWorkflowSubmitManager
class LEMEquipmentReservationSubmitManager
{
    static void main(Args args)
    {
        // Validates reservation.validateForSubmission()
        // Opens WorkflowSubmitDialog
        // Activates workflow, changes status to PendingApproval
    }
}

// ≡ VSIAssetRequestFulfilAction
class LEMEquipmentFulfilAction
{
    // Dialog: select equipment matching model, can checkout
    // Calls EquipmentCheckoutHelper.checkout(equipmentId, requestor, actor, reservationId)
}
```

### EquipmentServiceRecord Workflow
```xpp
// ≡ VSIAssetMaintenanceWorkflow
class LEMEquipmentServiceWorkflowDocument extends WorkflowDocument
{
    queryName getQueryName() { return queryStr(LEMEquipmentServiceWorkflowQuery); }
}

// ≡ VSIAssetMaintenanceWorkflowEventHandler (3 interfaces)
class LEMEquipmentServiceWorkflowEventHandler implements
    WorkflowCanceledEventHandler,
    WorkflowCompletedEventHandler,
    WorkflowStartedEventHandler
{
    void started(WorkflowEventArgs args)
    {
        LEMEquipmentServiceRecord::changeStatusByRecId(
            args.parmWorkflowContext().parmRecId(),
            ServiceStatus::InService);  // ≡ sets to InProgress via status helper
    }
    void canceled(...) { changeStatusByRecId(recId, ServiceStatus::Reported); }
    void completed(...) { }
}

// ≡ VSIAssetMaintenanceRepairTaskEventHandler (7 interfaces for task)
class LEMEquipmentServiceTaskEventHandler implements
    WorkflowElementCanceledEventHandler,
    WorkflowElemChangeRequestedEventHandler,
    WorkflowElementCompletedEventHandler,
    WorkflowElementReturnedEventHandler,
    WorkflowElementStartedEventHandler,
    WorkflowWorkItemsCreatedEventHandler
{
    // Empty implementations (logic in outcome handlers)
}

// ≡ VSIAssetMaintenanceResolvedOutcomeHandler
class LEMEquipmentServiceCompletedHandler implements WorkflowElementCompletedEventHandler
{
    void completed(WorkflowElementEventArgs args)
    {
        LEMEquipmentServiceRecord::completeByRecId(
            args.parmWorkflowContext().parmRecId());
    }
}

// ≡ VSIAssetMaintenanceUnrepairableOutcomeHandler
class LEMEquipmentServiceUnserviceableHandler implements WorkflowElementDeniedEventHandler
{
    void denied(WorkflowElementEventArgs args)
    {
        LEMEquipmentServiceRecord::markUnserviceableByRecId(
            args.parmWorkflowContext().parmRecId());
    }
}

// ≡ VSIAssetMaintenanceWorkflowSubmitManager
class LEMEquipmentServiceSubmitManager
{
    static void main(Args args) { /* submit to workflow */ }
}
```

### EquipmentDecommission Workflow
```xpp
// ≡ VSIAssetRetirementWorkflow (identical structure to Reservation)
class LEMEquipmentDecommissionWorkflowDocument extends WorkflowDocument { ... }
class LEMEquipmentDecommissionWorkflowEventHandler implements ... { ... }
class LEMEquipmentDecommissionApprovalEventHandler implements ... { ... }
class LEMEquipmentDecommissionSubmitManager { ... }
```

---

## Custom Services (Shared Executor Pattern)

### Service Contracts
```xpp
// ≡ VSIAssetServiceRequest/Response interfaces
interface LEMEquipmentServiceRequest { str companyId(); }
interface LEMEquipmentServiceResponse 
{ 
    void setCompany(str); 
    void markSuccess(str); 
    void markFailure(List); 
}

// ≡ VSIAssetAssignRequestContract
[DataContract]
class LEMEquipmentCheckoutRequestContract implements LEMEquipmentServiceRequest
{
    str companyId;
    EquipmentId equipmentId;
    EquipmentTag equipmentTag;
    PersonnelId personnelId;
    PersonnelId performedByPersonnelId;
    ReservationId reservationId;
}

// ≡ VSIAssetAssignmentResponseContract
[DataContract]
class LEMEquipmentCheckoutResponseContract implements LEMEquipmentServiceResponse
{
    boolean success; str message; List errors; str dataAreaId;
    CheckoutId checkoutId; EquipmentId equipmentId; EquipmentTag equipmentTag;
    str equipmentStatus; PersonnelId personnelId;
    int calibrationInterval; int calibrationsDue;  // ≡ seatCount, seatsInUse
}

// ≡ VSIAssetDetailsRequestContract
[DataContract]
class LEMEquipmentDetailsRequestContract implements LEMEquipmentServiceRequest
{ str companyId; EquipmentId equipmentId; EquipmentTag equipmentTag; }

// ≡ VSIAssetDetailsResponseContract
[DataContract]
class LEMEquipmentDetailsResponseContract implements LEMEquipmentServiceResponse
{
    boolean success; str message; List errors; str dataAreaId;
    EquipmentId equipmentId; EquipmentTag equipmentTag; EquipmentModelId modelId;
    Name modelName; str equipmentClass; str status;
    SerialNumber serialNumber; Manufacturer manufacturer; Model model;
    LabLocationId locationId; Name locationName;
    VendorId vendorId; Name vendorName;
    str purchaseDate; str warrantyExpiryDate; int warrantyDaysRemaining;
    boolean isCalibrated; int calibrationInterval; int calibrationsDue;
    str nextCalibrationDate;
    boolean hasOpenService; ServiceId openServiceId; str openServiceStatus;
    List holders;  // List of LEMEquipmentHolderContract
}

// ≡ VSIWorkerAssetsRequestContract
[DataContract]
class LEMPersonnelEquipmentRequestContract implements LEMEquipmentServiceRequest
{ str companyId; PersonnelId personnelId; boolean allCompanies; }

// ≡ VSIWorkerAssetsResponseContract
[DataContract]
class LEMPersonnelEquipmentResponseContract implements LEMEquipmentServiceResponse
{
    boolean success; str message; List errors; str dataAreaId;
    PersonnelId personnelId; Name personnelName; PersonnelNumber personnelNumber;
    str employmentStatus; int equipmentCount; List equipment;
}
```

### Service Processor & Helper
```xpp
// ≡ VSIAssetServiceProcessor
interface LEMEquipmentServiceProcessor
{
    void process(str operation, LEMEquipmentServiceRequest request, LEMEquipmentServiceResponse response);
}

// ≡ VSIAssetServiceHelper (CRITICAL PATTERN)
class LEMEquipmentServiceHelper
{
    public static void execute(
        LEMEquipmentServiceProcessor processor,
        str operation,
        LEMEquipmentServiceRequest request,
        LEMEquipmentServiceResponse response)
    {
        int infologStart = infologLine();
        str company;
        #OCCRetryCount
        
        try
        {
            if (!request) throw error("Request missing");
            company = LEMEquipmentServiceHelper::resolveCompany(request.companyId());
            response.setCompany(company);
            
            changecompany(company)
            {
                ttsbegin;
                processor.process(operation, request, response);
                ttscommit;
            }
        }
        catch (Exception::Deadlock)
        {
            if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < #RetryNum) retry;
            response.markFailure(LEMEquipmentServiceHelper::failureMessages(infologStart, "Concurrency conflict"));
        }
        catch (Exception::UpdateConflict)
        {
            if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < #RetryNum) retry;
            response.markFailure(LEMEquipmentServiceHelper::failureMessages(infologStart, "Concurrency conflict"));
        }
        catch (Exception::Error)
        {
            response.markFailure(LEMEquipmentServiceHelper::failureMessages(infologStart, ''));
        }
        catch
        {
            response.markFailure(LEMEquipmentServiceHelper::failureMessages(infologStart, "Unexpected error"));
        }
    }
    
    static str resolveCompany(str dataAreaId) { /* validate legal entity */ }
    static LEMEquipment findEquipment(EquipmentId, EquipmentTag) { /* find by ID or tag */ }
    static void validateActor(PersonnelId actorId) { /* must be active */ }
    static List collectInfolog(int fromLine) { /* move infolog to list */ }
    static List failureMessages(int fromLine, str lead) { /* build error list */ }
    static str firstMessage(List messages) { /* get first error */ }
    static str formatDate(date) { /* yyyy-MM-dd */ }
    static str formatDateTime(utcdatetime) { /* ISO 8601 */ }
    static str enumSymbol(EnumId, int value) { return enum2Symbol(EnumId, value); }
}
```

### Checkout Service (≡ VSIAssetAssignmentService)
```xpp
// ≡ VSIAssetAssignmentService
class LEMEquipmentCheckoutService implements LEMEquipmentServiceProcessor
{
    public LEMEquipmentCheckoutResponseContract checkoutEquipment(LEMEquipmentCheckoutRequestContract request)
    {
        LEMEquipmentCheckoutResponseContract response = new LEMEquipmentCheckoutResponseContract();
        LEMEquipmentServiceHelper::execute(this, methodStr(...), request, response);
        return response;
    }
    
    public void process(str operation, LEMEquipmentServiceRequest request, LEMEquipmentServiceResponse response)
    {
        switch (operation)
        {
            case methodStr(LEMEquipmentCheckoutService, checkoutEquipment):
                processCheckout(request, response);
                break;
            default: throw error("Unknown operation");
        }
    }
    
    private void processCheckout(LEMEquipmentCheckoutRequestContract req, LEMEquipmentCheckoutResponseContract resp)
    {
        // Validate actor, find equipment, check canCheckout
        // If reservationId: validate reservation, personnel match
        // Call EquipmentCheckoutHelper.checkout()
        // Fill response with equipment state
    }
}
```

### Inquiry Service (≡ VSIAssetInquiryService)
```xpp
// ≡ VSIAssetInquiryService
class LEMEquipmentInquiryService implements LEMEquipmentServiceProcessor
{
    public LEMEquipmentDetailsResponseContract getEquipmentDetails(LEMEquipmentDetailsRequestContract req) { ... }
    public LEMPersonnelEquipmentResponseContract getPersonnelEquipment(LEMPersonnelEquipmentRequestContract req) { ... }
    
    public void process(str operation, request, response)
    {
        switch (operation)
        {
            case methodStr(..., getEquipmentDetails): processDetails(request, response); break;
            case methodStr(..., getPersonnelEquipment): processPersonnel(request, response); break;
        }
    }
    
    private void processDetails(req, resp)
    {
        // Find equipment, load model, location, vendor, calibration
        // Get open checkouts (holders)
        // Get open service record
        // Fill all fields, markSuccess
    }
    
    private void processPersonnel(req, resp)
    {
        // Cross-company query if allCompanies
        // Join checkouts + equipment + model
        // Build LEMEquipmentLineContract list
    }
}
```

### Service Catalog & Test Harness (≡ VSIAssetServiceCatalog)
```xpp
class LEMEquipmentServiceCatalog
{
    static void populate(LEMEquipmentServiceOperationTmp ops) { /* 3 operations */ }
    static str endpointUrl(str service, str operation) { /* build URL from host */ }
    static boolean isWriteOperation(str op) { return op == "checkoutEquipment"; }
    static str sampleRequest(str op) { /* build JSON from live data */ }
    static str sampleResponse(str op) { /* live for reads, mock for write */ }
    static str runTest(str op, str json) { /* deserialize, call service, return JSON */ }
    // ... prettyPrint, extractRequest, wrapRequest, failureJson, clrMessage
    // ... sample data helpers (sampleEquipmentId, samplePersonnelId, etc.)
}
```

---

## Batch Processing (Runtime Tasks Pattern)

### EquipmentIntegrityAuditBatch (≡ VSIAssetIntegrityAuditBatch)
```xpp
// Contract with: checkReservations, approvedReservationDays, notifyLabManagers, bundleSize
// Controller: BatchRetryable, constructs with service class
// Service: process() splits equipment into bundles, dispatches runtime tasks
//          + optional reservation check task
// Task Controller: parmShowDialog(false), BatchRetryable
// Task Contract: fromRecId, toRecId, isReservationCheck, runDate, approvedDays, notify
// UI Builder: field overrides for validation, checkRequests enables approvedDays
// Findings: collects, logs, summarizes with digest()

// Integrity Checks (15 ≡ VSI):
enum EquipmentIntegrityCheck
{
    CheckedOutWithoutHolder,        // ≡ AssignedWithoutCustodian
    AvailableWithOpenCheckout,      // ≡ InStockWithOpenAssignment
    DecommissionedWithOpenCheckout, // ≡ RetiredWithOpenAssignment
    InServiceWithoutServiceRecord,  // ≡ UnderRepairWithoutTicket
    MultipleHolders,                // ≡ MultipleCustodians
    CalibrationOverdue,             // ≡ LicenseSeatsExceeded
    StatusLogMismatch,              // ≡ StatusHistoryMismatch
    MissingStatusLog,               // ≡ MissingStatusHistory
    CalibrationDetailMismatch,      // ≡ LicenseDetailMismatch
    ServiceOnConsumable,            // ≡ MaintenanceOnLicense
    DecommissionedWithoutApproval,  // ≡ RetiredWithoutApproval
    ApprovedNotDecommissioned,      // ≡ ApprovedNotRetired
    InactivePersonnelHolds,         // ≡ InactiveWorkerHolds
    FulfilledWithoutCheckout,       // ≡ FulfilledWithoutAssignment
    ApprovedNotFulfilled            // ≡ ApprovedNotFulfilled
}
```

### StaleEquipmentDetectionBatch (≡ VSIStaleAssetDetectionBatch)
```xpp
// Contract: availableStaleDays, labLocationId, serviceStaleDays, notifyTechnicians
// Detects: Available equipment with no status change > threshold
//          Open service records not updated > threshold
// Notifies: Lab managers + technicians (per-technician digest)
```

### CalibrationExpiryAlertBatch (≡ VSIWarrantyExpiryAlertBatch)
```xpp
// Contract: daysAhead, reminderIntervalDays, equipmentModelId, bundleSize
// Bundles: 64 max runtime tasks
// Process: finds equipment with warranty/calibration expiry in window
//          Stamps LastCalibrationAlertDate
//          Sends notification with holder/location info
```

### CalibrationRenewalAlertBatch (≡ VSILicenseRenewalAlertBatch)
```xpp
// Contract: daysAhead, reminderIntervalDays, equipmentModelId (Calibrated only)
// Process: finds Calibrated-class equipment with NextCalibrationDate in window
//          Stamps LastCalibrationAlertDate
//          Notifies lab managers with calibration interval, calibrations due
```

---

## Reporting (Multi-Temp Table Pattern)

### Report 7: EquipmentOverviewReport (≡ VSIAssetOverviewReport)
```xpp
// Contract: asOfDate, monthsBack, daysAhead
// DP: LEMEquipmentOverviewDP (extends SRSReportDataProviderBase)
// Temp Tables:
class LEMEquipmentOverviewKpiTmp    // ≡ VSIAssetOverviewKpiTmp
class LEMEquipmentOverviewChartTmp  // ≡ VSIAssetOverviewChartTmp
class LEMEquipmentOverviewAttentionTmp // ≡ VSIAssetOverviewAttentionTmp

// Passes (6):
1. Equipment as of date: status mix, class×status, location×status, dept×checkedout, idle age
2. Utilization trend at month ends
3. Lifecycle: registrations, checkouts, decommissions per month
4. Expiry: warranty + calibration (12 months forward)
5. Calibration: intervals vs due per equipment
6. Service: tickets, turnaround, cost, status, technician load

// Attention list: Expiring (soonest first), OpenService (longest open), LongIdle (>90 days)
// Top 10 per type, KPI tiles show full counts
```

### Report 6: EquipmentUtilizationReport (≡ VSIAssetUtilizationReport)
```xpp
// Contract: asOfDate, filterByClass, equipmentClass
// DP: LEMEquipmentUtilizationDP
// Temp: LEMEquipmentUtilizationTmp
// Buckets: Class → Location → Department
// Metrics: Total, CheckedOut, Available, InService, IdleDays, MaxIdle
```

### Report 3: CalibrationWarrantyExpiryReport (≡ VSILicenseWarrantyExpiryReport)
```xpp
// Contract: asOfDate, daysAhead
// DP: LEMEquipmentCalibrationWarrantyExpiryDP
// Temp: LEMEquipmentCalibrationWarrantyExpiryTmp
// Sources: Equipment (warranty) + EquipmentCalibration (calibration)
// Filters: non-Consumable for warranty, Calibrated for calibration
```

### Report 5: EquipmentStatusAuditTrail (≡ VSIAssetStatusAuditTrailReport)
```xpp
// Contract: equipmentId, fromDate, toDate
// DP: LEMEquipmentStatusAuditTrailDP
// Temp: LEMEquipmentStatusAuditTrailTmp
// Matrix: Equipment × Status days (pivot)
// List: Chronological status changes with reason, source refs, days in status
```

### Report 2: EquipmentRegisterReport (≡ VSIAssetRegisterReport)
```xpp
// Query: LEMEquipmentRegisterQuery
// Groups: Class → Location
// Columns: EquipmentTag, Model, Serial, Status, Location, CurrentHolder
```

### Report 1: EquipmentServiceHistoryReport (≡ VSIAssetMaintenanceHistoryReport)
```xpp
// Query: LEMEquipmentServiceHistoryQuery
// Group by equipment, sort by date
// Columns: ServiceId, Date, Technician, Issue, Status, CompletedDate, TurnaroundDays, Cost
```

### Report 2b: EquipmentTagLabelReport (≡ VSIAssetTagLabelReport)
```xpp
// Controller: LEMEquipmentTagLabelController (no dialog, uses selection)
// Query: LEMEquipmentTagQuery
// Layout: Code 128 barcode, EquipmentTag, Model, Serial, Class/Location
// Page break per equipment
```

---

## Forms (Pattern Mapping)

### EquipmentDetails (≡ VSIAssetDetails)
```xpp
// Custom form with tabs:
// - Overview (grid)
// - Details: General, Checkout, Warranty, Calibration
// - History tabs: Checkout, Service, Status
// ActionPane: Checkout/Checkin/Transfer, RequestService, Decommission, PrintTag
// NumberSeqFormHandler for EquipmentId
// updateDesign(): visibility by EquipmentClass, status, Calibrated
```

### EquipmentListPage (≡ VSIAssetListPage)
```xpp
// ListPage with CustomFilterGroup:
// Filters: Model, Vendor, Status, Location (with descendants), Custodian
// FactBox Parts: Calibration, Checkout, Service
// Actions: New, ViewDetails, Checkout/Checkin/Transfer, PrintTag
// exists join for custodian filter (same pattern)
```

### EquipmentService (≡ VSIAssetMaintenance)
```xpp
// SimpleListDetails-Grid + Workflow enabled
// WorkflowType: LEMEquipmentServiceWorkflow
// NumberSeqFormHandler for ServiceId
// init(): locks to current technician if opened from "My Services"
// active(): field/button enablement by status
// Actions: StartService, DecommissionEquipment
```

### EquipmentReservation (≡ VSIAssetRequest)
```xpp
// Custom + Workflow (LEMEquipmentReservationWorkflow)
// NumberSeqFormHandler for ReservationId
// init(): locks to requestor (My Reservations) or status=Approved (Fulfilment Queue)
// active(): edit/delete only Draft; Fulfil button enabled if canFulfil()
// Fulfil action: dialog with equipment lookup (filtered by model, status)
```

### EquipmentDecommission (≡ VSIAssetRetirement)
```xpp
// Custom + Workflow (LEMEquipmentDecommissionWorkflow)
// NumberSeqFormHandler for DecommissionId
// initValue(): copies equipment, service from caller
// modifiedField(EquipmentId): sets defaults (DisposalMethod=NotApplicable for Consumable, DataWipeConfirmed=No for non-serial)
// Reopen button: enabled if Rejected and equipment still decommissionable
```

### LabLocation (≡ VSIFunctionalLocation)
```xpp
// SimpleListDetails-Tree
// run(): buildTree(currentRecId)
// buildTree(): recursive parent-child map, sync selection
// createLocation(parentId): creates child under selected
// lookup for ParentLocationId: excludes self + descendants
// active(): locks LocationId after save; NewChild enabled for saved records
```

### EquipmentVendor / LabPersonnel (≡ VSIVendor / VSIWorker)
```xpp
// SimpleList (Vendor) / SimpleListDetails-Grid (Personnel)
// NumberSeqFormHandler for VendorId/PersonnelId (global sequences)
// create/write/validateWrite/linkActive/active/delete with number sequence handling
// active(): locks VendorAccountNum/PersonnelNumber after save
```

### EquipmentServiceEndpoints (≡ VSIAssetServiceEndpoints)
```xpp
// SimpleListDetails with side panel navigation
// Shows: endpoint URL, direction, sample request/response JSON
// Buttons: Test (runs JSON), ResetSample
// InMemory temp table: LEMEquipmentServiceOperationTmp
```

---

## Number Sequences (8 References)

| EDT | Scope | Sort | Help Text |
|-----|-------|------|-----------|
| LEMEquipmentId | Company | 1 | Unique equipment ID |
| LMReservationId | Company | 2 | Unique reservation ID |
| LMServiceId | Company | 3 | Unique service ID |
| LMDecommissionId | Company | 4 | Unique decommission ID |
| LMCheckoutId | Company | 5 | Unique checkout ID |
| LMStatusHistoryId | Company | 6 | Unique status history ID |
| LMPersonnelId | **Global** | 7 | Unique personnel ID |
| LMVendorId | **Global** | 8 | Unique vendor ID |

Registered via `LEMEquipmentNumberSeqModule extends NumberSeqApplicationModule`
Module: `NumberSeqModule::LMEquipmentManagement` (enum extension)

---

## Notifications (Action Center)

### LEMEquipmentNotificationHelper (≡ VSIAssetNotificationHelper)
```xpp
class LEMEquipmentNotificationHelper
{
    const str RuleId = 'LMEquipmentManagement';
    
    // Lab managers with active sign-in
    static List labManagerUserIds()
    {
        // Join LabPersonnel (IsLabManager=Yes, Active) + UserInfo (enabled)
    }
    
    // Active personnel user ID
    static UserId activePersonnelUserId(PersonnelId _personnelId)
    {
        // Join LabPersonnel + UserInfo
    }
    
    // Truncate to 1000 chars
    // NotifyUsers(List, title, message) via SystemNotificationsManager
}
```

Used by:
- Batch jobs (integrity, stale, calibration alerts)
- Workflow outcome handlers (optional)

---

## Security Model

### Duty: LMEquipmentManagementMaintain (≡ VSIAssetManagementMaintain)
- 30+ privileges covering all forms, entities, services

### Privileges (52)
- Form Maintain/View: 16 forms × 2
- Entity Maintain/View: 11 entities × 2
- Service Invoke: LMEquipmentCheckoutServiceInvoke, LMEquipmentInquiryServiceInvoke

### Role: LMEquipmentAdministrator (≡ VSIAssetAdministratorRole)
- Duty: LMEquipmentManagementMaintain

---

## Data Entities (11)

| Entity | Staging | Category | Key | Special |
|--------|---------|----------|-----|---------|
| LEMEquipmentEntity | LEMEquipmentStaging | Reference | EquipmentTag+DataAreaId | |
| LEMEquipmentModelEntity | LEMEquipmentModelStaging | Reference | EquipmentModelId+DataAreaId | |
| LEMLabLocationEntity | LEMLabLocationStaging | Reference | LabLocationId+DataAreaId | |
| LEMEquipmentVendorEntity | LEMEquipmentVendorStaging | Reference | VendorAccountNum | mapEntityToDataSource: Insert→nextVendorId(), Update→orig() |
| LEMLabPersonnelEntity | LEMLabPersonnelStaging | Reference | PersonnelNumber | mapEntityToDataSource: Insert→nextPersonnelId(), Update→orig() |
| LEMEquipmentCalibrationEntity | LEMEquipmentCalibrationStaging | Reference | EquipmentTag+DataAreaId | Embedded Equipment for tag |
| LEMEquipmentReservationEntity | LEMEquipmentReservationStaging | Document | ReservationId+DataAreaId | |
| LEMEquipmentServiceEntity | LEMEquipmentServiceStaging | Transaction | ServiceId+DataAreaId | |
| LEMEquipmentDecommissionEntity | LEMEquipmentDecommissionStaging | Transaction | DecommissionId+DataAreaId | |
| LEMEquipmentCheckoutEntity | LEMEquipmentCheckoutStaging | Transaction | CheckoutId+DataAreaId | |
| LEMEquipmentStatusLogEntity | LEMEquipmentStatusLogStaging | Transaction | LogId+DataAreaId | |

---

## Queries (6)

| Query | Purpose |
|-------|---------|
| LEMEquipmentServiceHistoryQuery | Report 1: Service with equipment + technician |
| LEMEquipmentServiceWorkflowQuery | Workflow doc for service |
| LEMEquipmentRegisterQuery | Report 2: Register with model + location |
| LEMEquipmentReservationWorkflowQuery | Workflow doc for reservations |
| LEMEquipmentDecommissionWorkflowQuery | Workflow doc for decommissions |
| LEMEquipmentTagQuery | Report 2b: Tag labels with model + location |

---

## Key Pattern Preservation Checklist

✅ **Status Change Guard**: `LEMEquipmentStatusChangeContext` (IDisposable singleton)  
✅ **Document Status Guard**: `LEMDocumentStatusChangeContext` for workflow docs  
✅ **Assignment Logic**: `LEMEquipmentCheckoutHelper` (checkout/checkin/transfer with calibration seat logic)  
✅ **Workflow Events**: 7 interfaces for approvals, 7 for tasks, 3 for lifecycles  
✅ **Service Executor**: `LEMEquipmentServiceHelper.execute()` with retry, infolog, changecompany  
✅ **Batch Runtime Tasks**: Splitting + bundling + task controllers (`parmShowDialog(false)`)  
✅ **Cross-Company**: `companies()` method with `changecompany`  
✅ **NumberSeqModule**: 8 references, global for Personnel/Vendor  
✅ **Entity Mapping**: `mapEntityToDataSource` for global sequences (Personnel, Vendor)  
✅ **Tree Form**: Recursive `buildTree` + `selectionChanged` sync  
✅ **Report Temp Tables**: KPI + Chart + Attention (Report 7)  
✅ **Notifications**: Admin lookup + truncation + Action Center  
✅ **Form Overrides**: `registerOverrideMethod` for lookups, validation, modified  
✅ **MultiSelectionHelper**: Range building for report controllers  
✅ **SysQueryRangeUtil**: Date/month ranges in report DPs  
✅ **Service Catalog**: Endpoint URLs, sample JSON, in-process test harness  

---

## Conclusion

The **Laboratory Equipment Management System (LEMS)** demonstrates that the VSI Asset Management architecture is a **domain-agnostic framework** for:

1. **Trackable asset lifecycles** with state machines
2. **Assignment/transfer** with single/multi-holder support
3. **Workflow-driven business processes** (request → approve → fulfill)
4. **Service/maintenance management** with technician assignment
5. **Compliance/retirement** with approval chains
6. **Audit trails** with immutable history
7. **Batch integrity monitoring** with parallel processing
8. **Integration-ready services** with shared execution infrastructure
9. **Hierarchical location management**
10. **Comprehensive reporting** with attention-based KPIs

**Every single class, method, and pattern in VSI has a direct LEMS equivalent** — proving the architecture's reusability across equipment-intensive domains (manufacturing, healthcare, research, IT, facilities, etc.).

---

## Appendix: File Structure Mapping

```
LEMS Project Structure (mirrors VSI):
├── AxClass\
│   ├── LEMEquipmentCheckoutAction.xml
│   ├── LEMEquipmentCheckoutHelper.xml
│   ├── LEMEquipmentStatusHelper.xml
│   ├── LEMEquipmentStatusChangeContext.xml
│   ├── LEMDocumentStatusChangeContext.xml
│   ├── LEMEquipmentCheckoutService.xml
│   ├── LEMEquipmentInquiryService.xml
│   ├── LEMEquipmentServiceHelper.xml
│   ├── LEMEquipmentServiceCatalog.xml
│   ├── LEMEquipmentIntegrityAuditBatch*.xml (6 files)
│   ├── LEMEquipmentStaleDetectionBatch*.xml (4 files)
│   ├── LEMEquipmentCalibrationAlertBatch*.xml (4 files)
│   ├── LEMEquipmentCalibrationRenewalBatch*.xml (4 files)
│   ├── LEMEquipmentCheckoutRequestContract.xml
│   ├── LEMEquipmentCheckoutResponseContract.xml
│   ├── LEMEquipmentDetailsRequestContract.xml
│   ├── LEMEquipmentDetailsResponseContract.xml
│   ├── LEMEquipmentHolderContract.xml
│   ├── LEMEquipmentLineContract.xml
│   ├── LEMPersonnelEquipmentRequestContract.xml
│   ├── LEMPersonnelEquipmentResponseContract.xml
│   ├── LEMEquipmentNotificationHelper.xml
│   ├── LEMEquipmentNumberSeqModule.xml
│   ├── LEMEquipmentOverviewDP.xml
│   ├── LEMEquipmentUtilizationDP.xml
│   ├── LEMEquipmentCalibrationWarrantyExpiryDP.xml
│   ├── LEMEquipmentStatusAuditTrailDP.xml
│   ├── LEMEquipmentReportHelper.xml
│   ├── LEMEquipmentWorkflowActorHelper.xml
│   ├── LEMLabPersonnelHelper.xml
│   └── ... (workflow handlers, batch constants, etc.)
├── AxTable\ (12 core + 12 staging + 3 temp + 3 tmp)
├── AxDataEntityView\ (11 entities)
├── AxForm\ (15 forms)
├── AxReport\ (7 reports)
├── AxWorkflowTemplate\ (3 workflows)
├── AxWorkflowApproval\ (2 approvals)
├── AxWorkflowTask\ (1 task)
├── AxWorkflowCategory\ (1 category)
├── AxMenu\ (1 menu)
├── AxService\ (2 services)
├── AxServiceGroup\ (1 group)
├── AxEnum\ (17 enums)
├── AxEnumExtension\ (1 extension)
├── AxEdt\ (19 EDTs)
├── AxQuery\ (6 queries)
├── AxSecurityDuty\ (1 duty)
├── AxSecurityPrivilege\ (52 privileges)
├── AxSecurityRole\ (1 role)
└── AxLabelFile\ (1 label file)
```