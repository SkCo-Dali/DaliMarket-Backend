from fastapi import FastAPI

# Importa los routers de los endpoints de Users
from app.api.Users.listUsers import router as listUsersRouter
from app.api.Users.getUser import router as getUserRouter
from app.api.Users.createUser import router as createUserRouter
from app.api.Users.updateUser import router as updateUserRouter
from app.api.Users.deleteUser import router as deleteUserRouter
from app.api.Users.getUserRoles import router as getUserRolesRouter
from app.api.Users.searchUser import router as searchUserRouter
from app.api.Users.setUserStatus import router as setUserStatusRouter

# Importa los routers de los endpoints de Leads
from app.api.Leads.createLead import router as createLeadRouter
from app.api.Leads.listLeads import router as listLeadsRouter
#from app.api.Leads.getLead import router as getLeadRouter
from app.api.Leads.updateLead import router as updateLeadRouter
from app.api.Leads.deleteLead import router as deleteLeadRouter
from app.api.Leads.assignLead import router as assignLeadRouter
from app.api.Leads.updateLeadStage import router as updateLeadStageRouter
from app.api.Leads.getLeadsByUser import router as getLeadsByUserRouter
from app.api.Leads.bulkAssignLeads import router as bulkAssignLeadsRouter
from app.api.Leads.exportLeads import router as exportLeadsRouter
from app.api.Leads.getDuplicateLeads import router as getDuplicateLeadsRouter
from app.api.Leads.mergeLeads import router as mergeLeadsRouter
from app.api.Leads.bulkLeadFile import router as bulkLeadFileRouter

# Importa los routers de los endpoints de Lead Assignments
from app.api.LeadAssignments.leadReassignment import router as leadReassignmentRouter
from app.api.LeadAssignments.getLeadAssignmentHistory import router as getLeadAssignmentHistoryRouter
from app.api.LeadAssignments.getCurrentLeadAssignment import router as getCurrentLeadAssignmentRouter
from app.api.LeadAssignments.getLeadAssignmentHistoryOut import router as getLeadAssignmentHistoryOutRouter
from app.api.LeadAssignments.getLeadReassignable import router as getLeadReassignableRouter
from app.api.LeadAssignments.getLeadOrphaned import router as getLeadOrphanedRouter
from app.api.LeadAssignments.routes_leads import router as routes_leadsRouter
from app.api.LeadAssignments.routes_users import router as routes_usersRouter


# Importa los routers de los endpoints de Interactions
from app.api.Interactions.createInteractions import router as createInteractionsRouter
from app.api.Interactions.getInteractionsByLead import router as getInteractionsByLeadRouter
from app.api.Interactions.updateInteractions import router as updateInteractionsRouter
from app.api.Interactions.deleteInteractions import router as deleteInteractionsRouter
from app.api.Interactions.getInteractionsByUserId import router as getInteractionsByUserIdRouter
from app.api.Interactions.getInteractionsRecents import router as getInteractionsRecentsRouter
from app.api.Interactions.getClientHistory import router as getClientHistoryRouter


# Importa los routers de los endpoints de Emails
from app.api.Emails.sendEmails import router as sendEmailsRouter
from app.api.Emails.getEmails import router as getEmailsRouter
from app.api.Emails.getEmailTracker import router as getEmailTrackerRouter

# Importa los routers de los endpoints de Profiling
from app.api.Profiling.profiling import router as profilingRouter

# Importa los routers de los endpoints de Whatsapp
#from app.api.whatsapp.limits import router as limitsRouter
#from app.api.whatsapp.send_mass import router as sendMassRouter
#from app.api.whatsapp.templates import router as templatesRouter
#from app.api.whatsapp.webhooks import router as whatsappWebhooksRouter


app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "ok"}

# Incluyendo los routers

# Se invoca a los routers de Users
app.include_router(listUsersRouter)
app.include_router(getUserRolesRouter)
app.include_router(searchUserRouter)
app.include_router(getUserRouter)
app.include_router(createUserRouter)
app.include_router(setUserStatusRouter)
app.include_router(updateUserRouter)
app.include_router(deleteUserRouter)

# Se invoca a los routers de Leads
app.include_router(mergeLeadsRouter)
app.include_router(getDuplicateLeadsRouter)
app.include_router(exportLeadsRouter)
#app.include_router(getLeadRouter)
app.include_router(listLeadsRouter)
app.include_router(assignLeadRouter)
app.include_router(updateLeadRouter)
app.include_router(updateLeadStageRouter)
app.include_router(deleteLeadRouter)
app.include_router(getLeadsByUserRouter)
app.include_router(bulkAssignLeadsRouter)
app.include_router(exportLeadsRouter)
app.include_router(bulkLeadFileRouter)
app.include_router(createLeadRouter)

# Se invoca a los routers de Lead Assignments
app.include_router(leadReassignmentRouter)
app.include_router(getLeadAssignmentHistoryRouter)
app.include_router(getCurrentLeadAssignmentRouter)
app.include_router(getLeadAssignmentHistoryOutRouter)
app.include_router(getLeadReassignableRouter)
app.include_router(getLeadOrphanedRouter)
app.include_router(routes_leadsRouter)
app.include_router(routes_usersRouter)

# Se invoca a los routers de Interactions
app.include_router(createInteractionsRouter)
app.include_router(getInteractionsByLeadRouter)
app.include_router(updateInteractionsRouter)
app.include_router(deleteInteractionsRouter)
app.include_router(getInteractionsByUserIdRouter)
app.include_router(getInteractionsRecentsRouter)
app.include_router(getClientHistoryRouter)


# Se invoca a los routers de Emails
app.include_router(sendEmailsRouter)
app.include_router(getEmailsRouter)
app.include_router(getEmailTrackerRouter)

# Se invoca a los routers de Profiling
app.include_router(profilingRouter)

# Se invoca a los routers de Whatsapp
#app.include_router(limitsRouter)
#app.include_router(sendMassRouter)
#app.include_router(templatesRouter)
#app.include_router(whatsappWebhooksRouter)